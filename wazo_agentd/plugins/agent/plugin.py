# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .http import (
    _AddAgentToQueue,
    _AgentById,
    _AgentByNumber,
    _LoginAgentById,
    _LoginAgentByNumber,
    _LoginUserAgent,
    _LogoffAgentById,
    _LogoffAgentByNumber,
    _LogoffUserAgent,
    _PauseAgentByNumber,
    _PauseUserAgent,
    _RemoveAgentFromQueue,
    _UnpauseAgentByNumber,
    _UnpauseUserAgent,
    _UserAgent,
)


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        service_proxy = dependencies['service_proxy']

        api.add_resource(
            _AgentById,
            '/agents/by-id/<int:agent_id>',
            resource_class_args=[service_proxy],
        )

        api.add_resource(
            _AgentByNumber,
            '/agents/by-number/<agent_number>',
            resource_class_args=[service_proxy],
        )

        api.add_resource(
            _UserAgent,
            '/users/me/agents',
            resource_class_args=[service_proxy],
        )

        api.add_resource(
            _LoginAgentById,
            '/agents/by-id/<int:agent_id>/login',
            resource_class_args=[service_proxy],
        )

        api.add_resource(
            _LoginAgentByNumber,
            '/agents/by-number/<agent_number>/login',
            resource_class_args=[service_proxy],
        )

        api.add_resource(
            _LoginUserAgent,
            '/users/me/agents/login',
            resource_class_args=[service_proxy],
        )

        api.add_resource(
            _LogoffAgentById,
            '/agents/by-id/<int:agent_id>/logoff',
            resource_class_args=[service_proxy],
        )

        api.add_resource(
            _LogoffAgentByNumber,
            '/agents/by-number/<agent_number>/logoff',
            resource_class_args=[service_proxy],
        )

        api.add_resource(
            _LogoffUserAgent,
            '/users/me/agents/logoff',
            resource_class_args=[service_proxy],
        )

        api.add_resource(
            _PauseUserAgent,
            '/users/me/agents/pause',
            resource_class_args=[service_proxy],
        )

        api.add_resource(
            _UnpauseUserAgent,
            '/users/me/agents/unpause',
            resource_class_args=[service_proxy],
        )

        api.add_resource(
            _AddAgentToQueue,
            '/agents/by-id/<int:agent_id>/add',
            resource_class_args=[service_proxy],
        )

        api.add_resource(
            _RemoveAgentFromQueue,
            '/agents/by-id/<int:agent_id>/remove',
            resource_class_args=[service_proxy],
        )

        api.add_resource(
            _PauseAgentByNumber,
            '/agents/by-number/<agent_number>/pause',
            resource_class_args=[service_proxy],
        )

        api.add_resource(
            _UnpauseAgentByNumber,
            '/agents/by-number/<agent_number>/unpause',
            resource_class_args=[service_proxy],
        )
