# Copyright 2013-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import logging

from cheroot import wsgi
from flask import Flask
from flask import request
from flask_cors import CORS
from flask_restful import Api, Resource
from requests import HTTPError

from werkzeug.exceptions import BadRequest
from werkzeug.contrib.fixers import ProxyFix
from xivo_agent.exception import AgentServerError, NoSuchAgentError, NoSuchExtensionError, \
    AgentAlreadyLoggedError, ExtensionAlreadyInUseError, AgentNotLoggedError, \
    NoSuchQueueError, AgentAlreadyInQueueError, AgentNotInQueueError, ContextDifferentTenantError, \
    QueueDifferentTenantError
from xivo import http_helpers
from xivo.auth_verifier import AuthVerifier, required_acl
from xivo.http_helpers import ReverseProxied
from xivo.tenant_helpers import UnauthorizedTenant
from xivo.tenant_flask_helpers import Tenant, get_auth_client, get_token

from xivo_agent.swagger.resource import SwaggerResource

logger = logging.getLogger(__name__)


_AGENT_404_ERRORS = (
    NoSuchAgentError,
    NoSuchExtensionError,
    NoSuchQueueError,
)
_AGENT_409_ERRORS = (
    AgentAlreadyLoggedError,
    AgentNotLoggedError,
    AgentAlreadyInQueueError,
    AgentNotInQueueError,
    ExtensionAlreadyInUseError,
    ContextDifferentTenantError,
    QueueDifferentTenantError,
)


class AgentdAuthVerifier(AuthVerifier):

    def handle_unreachable(self, error):
        auth_client = self.client()
        message = ('Could not connect to authentication server on {client.host}:{client.port}: {error}'
                   .format(client=auth_client, error=error))
        logger.exception('%s', message)
        return {'error': message}, 503

    def handle_unauthorized(self, token):
        return {'error': 'invalid token or unauthorized'}, 401


auth_verifier = AgentdAuthVerifier()


def _common_error_handler(fun):
    def aux(*args, **kwargs):
        try:
            return fun(*args, **kwargs)
        except UnauthorizedTenant as e:
            return {'error': e.message}, 401
        except _AGENT_404_ERRORS as e:
            return {'error': e.error}, 404
        except _AGENT_409_ERRORS as e:
            return {'error': e.error}, 409
        except AgentServerError as e:
            return {'error': e.error}, 500

    return aux


def _extract_field(obj, key, type_):
    try:
        value = obj[key]
    except (KeyError, TypeError):
        raise BadRequest('missing key {}'.format(key))

    if not isinstance(value, type_):
        raise BadRequest('invalid type for key {}'.format(key))

    return value


def _extract_extension_and_context():
    obj = request.get_json()
    extension = _extract_field(obj, 'extension', str)
    context = _extract_field(obj, 'context', str)
    return extension, context


def _extract_queue_id():
    obj = request.get_json()
    queue_id = _extract_field(obj, 'queue_id', int)
    return queue_id


def _extract_reason():
    obj = request.get_json()
    reason = None
    if obj:
        reason = _extract_field(obj, 'reason', str)
        if len(reason) > 80:
            raise BadRequest('invalid value for key reason, max length 80')
    return reason


class _BaseResource(Resource):

    method_decorators = [auth_verifier.verify_token, _common_error_handler]

    def parse_params(self):
        params = {key: value for key, value in request.args.items()}
        if 'recurse' in params:
            params['recurse'] = params['recurse'] in ('True', 'true')

        return params

    def _build_tenant_list(self, params):
        tenant_uuid = Tenant.autodetect().uuid
        recurse = params.get('recurse', False)
        if not recurse:
            return [tenant_uuid]

        tenants = []
        auth_client = get_auth_client()
        token_object = get_token()
        auth_client.set_token(token_object.uuid)

        try:
            tenants = auth_client.tenants.list(tenant_uuid=tenant_uuid)['items']
        except HTTPError as e:
            response = getattr(e, 'response', None)
            status_code = getattr(response, 'status_code', None)
            if status_code == 401:
                return [tenant_uuid]
            raise

        return [t['uuid'] for t in tenants]


class _Agents(_BaseResource):

    @required_acl('agentd.agents.read')
    def get(self):
        params = self.parse_params()
        tenant_uuids = self._build_tenant_list(params)
        return self.service_proxy.get_agent_statuses(tenant_uuids=tenant_uuids)


class _AgentById(_BaseResource):

    @required_acl('agentd.agents.by-id.{agent_id}.read')
    def get(self, agent_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        return self.service_proxy.get_agent_status_by_id(agent_id, tenant_uuids=tenant_uuids)


class _AgentByNumber(_BaseResource):

    @required_acl('agentd.agents.by-number.{agent_number}.read')
    def get(self, agent_number):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        return self.service_proxy.get_agent_status_by_number(agent_number, tenant_uuids=tenant_uuids)


class _LoginAgentById(_BaseResource):

    @required_acl('agentd.agents.by-id.{agent_id}.login.create')
    def post(self, agent_id):
        extension, context = _extract_extension_and_context()
        tenant_uuids = self._build_tenant_list({'recurse': True})
        self.service_proxy.login_agent_by_id(agent_id, extension, context, tenant_uuids=tenant_uuids)
        return '', 204


class _LoginAgentByNumber(_BaseResource):

    @required_acl('agentd.agents.by-number.{agent_number}.login.create')
    def post(self, agent_number):
        extension, context = _extract_extension_and_context()
        tenant_uuids = self._build_tenant_list({'recurse': True})
        self.service_proxy.login_agent_by_number(agent_number, extension, context, tenant_uuids=tenant_uuids)
        return '', 204


class _LogoffAgentById(_BaseResource):

    @required_acl('agentd.agents.by-id.{agent_id}.logoff.create')
    def post(self, agent_id):
        # XXX logoff_agent_by_id raise a AgentNotLoggedError even if the agent doesn't exist;
        #     that means that logoff currently returns a 409 for an inexistant agent, not a 404
        tenant_uuids = self._build_tenant_list({'recurse': True})
        self.service_proxy.logoff_agent_by_id(agent_id, tenant_uuids=tenant_uuids)
        return '', 204


class _LogoffAgentByNumber(_BaseResource):

    @required_acl('agentd.agents.by-number.{agent_number}.logoff.create')
    def post(self, agent_number):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        self.service_proxy.logoff_agent_by_number(agent_number, tenant_uuids=tenant_uuids)
        return '', 204


class _LogoffAgents(_BaseResource):

    @required_acl('agentd.agents.logoff.create')
    def post(self):
        params = self.parse_params()
        tenant_uuids = self._build_tenant_list(params)
        self.service_proxy.logoff_all(tenant_uuids=tenant_uuids)
        return '', 204


class _AddAgentToQueue(_BaseResource):

    @required_acl('agentd.agents.by-id.{agent_id}.add.create')
    def post(self, agent_id):
        queue_id = _extract_queue_id()
        tenant_uuids = self._build_tenant_list({'recurse': True})
        self.service_proxy.add_agent_to_queue(agent_id, queue_id, tenant_uuids=tenant_uuids)
        return '', 204


class _RemoveAgentFromQueue(_BaseResource):

    @required_acl('agentd.agents.by-id.{agent_id}.delete.create')
    def post(self, agent_id):
        queue_id = _extract_queue_id()
        tenant_uuids = self._build_tenant_list({'recurse': True})
        self.service_proxy.remove_agent_from_queue(agent_id, queue_id, tenant_uuids=tenant_uuids)
        return '', 204


class _RelogAgents(_BaseResource):

    @required_acl('agentd.agents.relog.create')
    def post(self):
        params = self.parse_params()
        tenant_uuids = self._build_tenant_list(params)
        self.service_proxy.relog_all(tenant_uuids=tenant_uuids)
        return '', 204


class _PauseAgentByNumber(_BaseResource):

    @required_acl('agentd.agents.by-number.{agent_number}.pause.create')
    def post(self, agent_number):
        reason = _extract_reason()
        tenant_uuids = self._build_tenant_list({'recurse': True})
        self.service_proxy.pause_agent_by_number(agent_number, reason, tenant_uuids=tenant_uuids)
        return '', 204


class _UnpauseAgentByNumber(_BaseResource):

    @required_acl('agentd.agents.by-number.{agent_number}.unpause.create')
    def post(self, agent_number):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        self.service_proxy.unpause_agent_by_number(agent_number, tenant_uuids=tenant_uuids)
        return '', 204


class HTTPInterface:

    VERSION = '1.0'

    _resources = [
        (_Agents, '/agents'),
        (_AgentById, '/agents/by-id/<int:agent_id>'),
        (_AgentByNumber, '/agents/by-number/<agent_number>'),
        (_LoginAgentById, '/agents/by-id/<int:agent_id>/login'),
        (_LoginAgentByNumber, '/agents/by-number/<agent_number>/login'),
        (_LogoffAgentById, '/agents/by-id/<int:agent_id>/logoff'),
        (_LogoffAgentByNumber, '/agents/by-number/<agent_number>/logoff'),
        (_AddAgentToQueue, '/agents/by-id/<int:agent_id>/add'),
        (_RemoveAgentFromQueue, '/agents/by-id/<int:agent_id>/remove'),
        (_PauseAgentByNumber, '/agents/by-number/<agent_number>/pause'),
        (_UnpauseAgentByNumber, '/agents/by-number/<agent_number>/unpause'),
        (_LogoffAgents, '/agents/logoff'),
        (_RelogAgents, '/agents/relog'),
        (SwaggerResource, SwaggerResource.api_path),
    ]

    def __init__(self, config, service_proxy, auth_client):
        self._config = config['rest_api']
        self._app = Flask('xivo_agent')
        self._app.config.update(config)

        http_helpers.add_logger(self._app, logger)
        self._app.after_request(http_helpers.log_request)
        auth_verifier.set_client(auth_client)
        self._app.secret_key = os.urandom(24)
        self._load_cors()

        api = Api(self._app, prefix='/{}'.format(self.VERSION))
        self._add_resources(api, service_proxy)

    def _load_cors(self):
        cors_config = dict(self._config.get('cors', {}))
        enabled = cors_config.pop('enabled', False)
        if enabled:
            CORS(self._app, **cors_config)

    def _add_resources(self, api, service_proxy):
        for resource, url in self._resources:
            resource.service_proxy = service_proxy
            api.add_resource(resource, url)

    def run(self):
        config = self._config['https']
        bind_addr = (config['listen'], config['port'])

        wsgi_app = ReverseProxied(ProxyFix(self._app))
        server = wsgi.WSGIServer(bind_addr, wsgi_app)
        server.ssl_adapter = http_helpers.ssl_adapter(config['certificate'],
                                                      config['private_key'])
        try:
            server.start()
        finally:
            server.stop()
