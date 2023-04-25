# Copyright 2013-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import logging

from cheroot import wsgi
from flask import Flask
from flask import request
from flask_cors import CORS
from flask_restful import Api, Resource
from marshmallow import ValidationError

from werkzeug.middleware.proxy_fix import ProxyFix
from wazo_agentd.exception import (
    AgentServerError,
    NoSuchAgentError,
    NoSuchExtensionError,
    AgentAlreadyLoggedError,
    ExtensionAlreadyInUseError,
    AgentNotLoggedError,
    NoSuchQueueError,
    NoSuchLineError,
    AgentAlreadyInQueueError,
    AgentNotInQueueError,
    ContextDifferentTenantError,
    QueueDifferentTenantError,
)
from xivo import http_helpers
from xivo.auth_verifier import AuthVerifier, required_acl
from xivo.http_helpers import ReverseProxied
from xivo.tenant_helpers import UnauthorizedTenant
from xivo.tenant_flask_helpers import Tenant, token

from wazo_agentd.swagger.resource import SwaggerResource
from wazo_agentd.schemas import (
    agent_login_schema,
    pause_schema,
    queue_schema,
    user_agent_login_schema,
)

logger = logging.getLogger(__name__)


_AGENT_404_ERRORS = (NoSuchAgentError, NoSuchExtensionError, NoSuchQueueError)
_AGENT_409_ERRORS = (
    AgentAlreadyLoggedError,
    AgentNotLoggedError,
    AgentAlreadyInQueueError,
    AgentNotInQueueError,
    ExtensionAlreadyInUseError,
)
_AGENT_400_ERRORS = (
    ContextDifferentTenantError,
    NoSuchLineError,
    QueueDifferentTenantError,
)


_status_aggregator = None


class AgentdAuthVerifier(AuthVerifier):
    def handle_unreachable(self, error):
        auth_client = self.client()
        message = (
            f'Could not connect to authentication server '
            f'on {auth_client.host}:{auth_client.port}: {error}'
        )
        logger.exception('%s', message)
        return {'error': message}, 503

    def _handle_invalid_token_exception(self, token, required_access=None):
        return self.handle_unauthorized(token, required_access)

    def _handle_missing_permissions_token_exception(self, token, required_access=None):
        return self.handle_unauthorized(token, required_access)

    def handle_unauthorized(self, token, required_access=None):
        return {'error': 'invalid token or unauthorized'}, 401


auth_verifier = AgentdAuthVerifier()


def _common_error_handler(fun):
    def aux(*args, **kwargs):
        try:
            return fun(*args, **kwargs)
        except ValidationError as e:
            return {'error': 'invalid fields: ' + ', '.join(e.messages.keys())}, 400
        except _AGENT_400_ERRORS as e:
            return {'error': e.error}, 400
        except UnauthorizedTenant as e:
            return {'error': e.message}, 401
        except _AGENT_404_ERRORS as e:
            return {'error': e.error}, 404
        except _AGENT_409_ERRORS as e:
            return {'error': e.error}, 409
        except AgentServerError as e:
            return {'error': e.error}, 500

    return aux


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
        return [tenant.uuid for tenant in token.visible_tenants(tenant_uuid)]


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
        return self.service_proxy.get_agent_status_by_id(
            agent_id, tenant_uuids=tenant_uuids
        )


class _AgentByNumber(_BaseResource):
    @required_acl('agentd.agents.by-number.{agent_number}.read')
    def get(self, agent_number):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        return self.service_proxy.get_agent_status_by_number(
            agent_number, tenant_uuids=tenant_uuids
        )


class _StatusChecker(_BaseResource):
    @required_acl('agentd.status.read')
    def get(self):
        global _status_aggregator
        return _status_aggregator.status(), 200


class _UserAgent(_BaseResource):
    @required_acl('agentd.users.me.agents.read')
    def get(self):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        user_uuid = token.user_uuid
        return self.service_proxy.get_user_agent_status(
            user_uuid, tenant_uuids=tenant_uuids
        )


class _LoginAgentById(_BaseResource):
    @required_acl('agentd.agents.by-id.{agent_id}.login.create')
    def post(self, agent_id):
        body = agent_login_schema.load(request.get_json())
        tenant_uuids = self._build_tenant_list({'recurse': True})
        self.service_proxy.login_agent_by_id(
            agent_id, body['extension'], body['context'], tenant_uuids=tenant_uuids
        )
        return '', 204


class _LoginAgentByNumber(_BaseResource):
    @required_acl('agentd.agents.by-number.{agent_number}.login.create')
    def post(self, agent_number):
        body = agent_login_schema.load(request.get_json())
        tenant_uuids = self._build_tenant_list({'recurse': True})
        self.service_proxy.login_agent_by_number(
            agent_number, body['extension'], body['context'], tenant_uuids=tenant_uuids
        )
        return '', 204


class _LoginUserAgent(_BaseResource):
    @required_acl('agentd.users.me.agents.login.create')
    def post(self):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        user_uuid = token.user_uuid
        body = user_agent_login_schema.load(request.get_json())
        self.service_proxy.login_user_agent(
            user_uuid, body['line_id'], tenant_uuids=tenant_uuids
        )
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
        self.service_proxy.logoff_agent_by_number(
            agent_number, tenant_uuids=tenant_uuids
        )
        return '', 204


class _LogoffUserAgent(_BaseResource):
    @required_acl('agentd.users.me.agents.logoff.create')
    def post(self):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        user_uuid = token.user_uuid
        self.service_proxy.logoff_user_agent(user_uuid, tenant_uuids=tenant_uuids)
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
        body = queue_schema.load(request.get_json())
        tenant_uuids = self._build_tenant_list({'recurse': True})
        self.service_proxy.add_agent_to_queue(
            agent_id, body['queue_id'], tenant_uuids=tenant_uuids
        )
        return '', 204


class _RemoveAgentFromQueue(_BaseResource):
    @required_acl('agentd.agents.by-id.{agent_id}.delete.create')
    def post(self, agent_id):
        body = queue_schema.load(request.get_json())
        tenant_uuids = self._build_tenant_list({'recurse': True})
        self.service_proxy.remove_agent_from_queue(
            agent_id, body['queue_id'], tenant_uuids=tenant_uuids
        )
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
        body = pause_schema.load(request.get_json())
        tenant_uuids = self._build_tenant_list({'recurse': True})
        self.service_proxy.pause_agent_by_number(
            agent_number, body['reason'], tenant_uuids=tenant_uuids
        )
        return '', 204


class _PauseUserAgent(_BaseResource):
    @required_acl('agentd.users.me.agents.pause.create')
    def post(self):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        body = pause_schema.load(request.get_json())
        user_uuid = token.user_uuid
        self.service_proxy.pause_user_agent(
            user_uuid, body['reason'], tenant_uuids=tenant_uuids
        )
        return '', 204


class _UnpauseAgentByNumber(_BaseResource):
    @required_acl('agentd.agents.by-number.{agent_number}.unpause.create')
    def post(self, agent_number):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        self.service_proxy.unpause_agent_by_number(
            agent_number, tenant_uuids=tenant_uuids
        )
        return '', 204


class _UnpauseUserAgent(_BaseResource):
    @required_acl('agentd.users.me.agents.unpause.create')
    def post(self):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        user_uuid = token.user_uuid
        self.service_proxy.unpause_user_agent(user_uuid, tenant_uuids=tenant_uuids)
        return '', 204


class HTTPInterface:
    VERSION = '1.0'

    _resources = [
        (_Agents, '/agents'),
        (_AgentById, '/agents/by-id/<int:agent_id>'),
        (_AgentByNumber, '/agents/by-number/<agent_number>'),
        (_UserAgent, '/users/me/agents'),
        (_LoginAgentById, '/agents/by-id/<int:agent_id>/login'),
        (_LoginAgentByNumber, '/agents/by-number/<agent_number>/login'),
        (_LoginUserAgent, '/users/me/agents/login'),
        (_LogoffAgentById, '/agents/by-id/<int:agent_id>/logoff'),
        (_LogoffAgentByNumber, '/agents/by-number/<agent_number>/logoff'),
        (_LogoffUserAgent, '/users/me/agents/logoff'),
        (_PauseUserAgent, '/users/me/agents/pause'),
        (_UnpauseUserAgent, '/users/me/agents/unpause'),
        (_AddAgentToQueue, '/agents/by-id/<int:agent_id>/add'),
        (_RemoveAgentFromQueue, '/agents/by-id/<int:agent_id>/remove'),
        (_PauseAgentByNumber, '/agents/by-number/<agent_number>/pause'),
        (_UnpauseAgentByNumber, '/agents/by-number/<agent_number>/unpause'),
        (_LogoffAgents, '/agents/logoff'),
        (_RelogAgents, '/agents/relog'),
        (_StatusChecker, '/status'),
        (SwaggerResource, SwaggerResource.api_path),
    ]

    def __init__(self, config, service_proxy, auth_client, status_aggregator):
        global _status_aggregator
        _status_aggregator = status_aggregator
        self._config = config['rest_api']
        self._app = Flask('wazo_agent')
        self._app.config.update(config)

        http_helpers.add_logger(self._app, logger)
        self._app.before_request(http_helpers.log_before_request)
        self._app.after_request(http_helpers.log_request)
        auth_verifier.set_client(auth_client)
        self._app.secret_key = os.urandom(24)
        self._load_cors()
        self.server = None

        api = Api(self._app, prefix=f'/{self.VERSION}')
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
        bind_addr = (self._config['listen'], self._config['port'])

        wsgi_app = ReverseProxied(ProxyFix(self._app))
        self.server = wsgi.WSGIServer(bind_addr, wsgi_app)
        if self._config['certificate'] and self._config['private_key']:
            logger.warning(
                'Using service SSL configuration is deprecated. Please use NGINX instead.'
            )
            self.server.ssl_adapter = http_helpers.ssl_adapter(
                self._config['certificate'], self._config['private_key']
            )
        self.server.start()

    def stop(self):
        if self.server:
            self.server.stop()
