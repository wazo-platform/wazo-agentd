# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import os

from cherrypy import wsgiserver
from flask import Flask
from flask import request
from flask.ext import restful
from flask_cors import CORS
from werkzeug.contrib.fixers import ProxyFix
from werkzeug.exceptions import BadRequest
from xivo_agent.exception import AgentServerError, NoSuchAgentError, NoSuchExtensionError, \
    AgentAlreadyLoggedError, ExtensionAlreadyInUseError, AgentNotLoggedError, \
    NoSuchQueueError, AgentAlreadyInQueueError, AgentNotInQueueError


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
)


def _common_error_handler(fun):
    def aux(*args, **kwargs):
        try:
            return fun(*args, **kwargs)
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
    extension = _extract_field(obj, 'extension', basestring)
    context = _extract_field(obj, 'context', basestring)
    return extension, context


def _extract_queue_id():
    obj = request.get_json()
    queue_id = _extract_field(obj, 'queue_id', int)
    return queue_id


class _BaseResource(restful.Resource):

    method_decorators = [_common_error_handler]


class _Agents(_BaseResource):

    def get(self):
        return self.service_proxy.get_agent_statuses()


class _AgentById(_BaseResource):

    def get(self, agent_id):
        return self.service_proxy.get_agent_status_by_id(agent_id)


class _AgentByNumber(_BaseResource):

    def get(self, agent_number):
        return self.service_proxy.get_agent_status_by_number(agent_number)


class _LoginAgentById(_BaseResource):

    def post(self, agent_id):
        extension, context = _extract_extension_and_context()
        self.service_proxy.login_agent_by_id(agent_id, extension, context)
        return '', 204


class _LoginAgentByNumber(_BaseResource):

    def post(self, agent_number):
        extension, context = _extract_extension_and_context()
        self.service_proxy.login_agent_by_number(agent_number, extension, context)
        return '', 204


class _LogoffAgentById(_BaseResource):

    def post(self, agent_id):
        # XXX logoff_agent_by_id raise a AgentNotLoggedError even if the agent doesn't exist;
        #     that means that logoff currently returns a 409 for an inexistant agent, not a 404
        self.service_proxy.logoff_agent_by_id(agent_id)
        return '', 204


class _LogoffAgentByNumber(_BaseResource):

    def post(self, agent_number):
        self.service_proxy.logoff_agent_by_number(agent_number)
        return '', 204


class _LogoffAgents(_BaseResource):

    def post(self):
        self.service_proxy.logoff_all()
        return '', 204


class _AddAgentToQueue(_BaseResource):

    def post(self, agent_id):
        queue_id = _extract_queue_id()
        self.service_proxy.add_agent_to_queue(agent_id, queue_id)
        return '', 204


class _RemoveAgentFromQueue(_BaseResource):

    def post(self, agent_id):
        queue_id = _extract_queue_id()
        self.service_proxy.remove_agent_from_queue(agent_id, queue_id)
        return '', 204


class _RelogAgents(_BaseResource):

    def post(self):
        self.service_proxy.relog_all()
        return '', 204


class _PauseAgentByNumber(_BaseResource):

    def post(self, agent_number):
        self.service_proxy.pause_agent_by_number(agent_number)
        return '', 204


class _UnpauseAgentByNumber(_BaseResource):

    def post(self, agent_number):
        self.service_proxy.unpause_agent_by_number(agent_number)
        return '', 204


class HTTPInterface(object):

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
    ]

    def __init__(self, config, service_proxy):
        app = Flask('xivo_agent')
        app.wsgi_app = ProxyFix(app.wsgi_app)
        app.secret_key = os.urandom(24)
        self._load_cors(app, config)
        api = restful.Api(app, prefix='/{}'.format(self.VERSION))
        self._add_resources(api, service_proxy)
        bind_addr = (config['listen'], config['port'])
        self._server = wsgiserver.CherryPyWSGIServer(bind_addr, app)

    def _load_cors(self, app, config):
        cors_config = dict(config.get('cors', {}))
        enabled = cors_config.pop('enabled', False)
        if enabled:
            CORS(app, **cors_config)

    def _add_resources(self, api, service_proxy):
        for Resource, url in self._resources:
            Resource.service_proxy = service_proxy
            api.add_resource(Resource, url)

    def run(self):
        try:
            self._server.start()
        finally:
            self._server.stop()
