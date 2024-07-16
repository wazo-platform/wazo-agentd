# Copyright 2013-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import os

from cheroot import wsgi
from flask import Flask, request
from flask_cors import CORS
from flask_restful import Api, Resource
from marshmallow import ValidationError
from werkzeug.middleware.proxy_fix import ProxyFix
from xivo import http_helpers
from xivo.auth_verifier import (
    AuthServerUnreachable,
    InvalidTokenAPIException,
    MissingPermissionsTokenAPIException,
)
from xivo.flask.auth_verifier import AuthVerifierFlask
from xivo.http_helpers import ReverseProxied
from xivo.tenant_flask_helpers import Tenant, token
from xivo.tenant_helpers import UnauthorizedTenant

from wazo_agentd.exception import (
    AgentAlreadyInQueueError,
    AgentAlreadyLoggedError,
    AgentNotInQueueError,
    AgentNotLoggedError,
    AgentServerError,
    ContextDifferentTenantError,
    ExtensionAlreadyInUseError,
    NoSuchAgentError,
    NoSuchExtensionError,
    NoSuchLineError,
    NoSuchQueueError,
    QueueDifferentTenantError,
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

auth_verifier = AuthVerifierFlask()


def _common_error_handler(fun):
    def aux(*args, **kwargs):
        try:
            return fun(*args, **kwargs)
        except ValidationError as e:
            return {'error': 'invalid fields: ' + ', '.join(e.messages.keys())}, 400
        except _AGENT_400_ERRORS as e:
            return {'error': e.error}, 400
        except (InvalidTokenAPIException, MissingPermissionsTokenAPIException):
            return {'error': 'invalid token or unauthorized'}, 401
        except UnauthorizedTenant as e:
            return {'error': e.message}, 401
        except _AGENT_404_ERRORS as e:
            return {'error': e.error}, 404
        except _AGENT_409_ERRORS as e:
            return {'error': e.error}, 409
        except AgentServerError as e:
            return {'error': e.error}, 500
        except AuthServerUnreachable as e:
            error = e.details['original_error']
            logger.exception(
                'Could not connect to authentication server on %s:%s: %s',
                e.details['auth_server_host'],
                e.details['auth_server_port'],
                error,
            )
            return {'error': error}, 503

    return aux


class AuthResource(Resource):
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


class HTTPInterface:
    VERSION = '1.0'

    def __init__(self, config, service_proxy, auth_client, status_aggregator):
        global _status_aggregator
        _status_aggregator = status_aggregator
        self._config = config['rest_api']
        self._app = Flask('wazo_agent')
        self._app.config.update(config)

        http_helpers.add_logger(self._app, logger)
        self._app.before_request(http_helpers.log_before_request)
        self._app.after_request(http_helpers.log_request)
        self._app.secret_key = os.urandom(24)
        self._load_cors()
        self.server = None

        self.api = Api(self._app, prefix=f'/{self.VERSION}')

    def _load_cors(self):
        cors_config = dict(self._config.get('cors', {}))
        enabled = cors_config.pop('enabled', False)
        if enabled:
            CORS(self._app, **cors_config)

    def run(self):
        bind_addr = (self._config['listen'], self._config['port'])

        wsgi_app = ReverseProxied(ProxyFix(self._app))
        self.server = wsgi.WSGIServer(
            bind_addr,
            wsgi_app,
            numthreads=self._config['max_threads'],
        )
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
