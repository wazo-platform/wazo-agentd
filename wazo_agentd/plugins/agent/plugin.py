# Copyright 2024-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .http import (
    AddAgentToQueue,
    AgentById,
    AgentByNumber,
    AgentQueuesById,
    AgentQueuesByNumber,
    LoginAgentById,
    LoginAgentByNumber,
    LoginUserAgent,
    LogoffAgentById,
    LogoffAgentByNumber,
    LogoffUserAgent,
    PauseAgentByNumber,
    PauseUserAgent,
    RemoveAgentFromQueue,
    UnpauseAgentByNumber,
    UnpauseUserAgent,
    UserAgent,
    UserQueues,
)


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        service_proxy = dependencies['service_proxy']

        api.add_resource(
            AgentById,
            '/agents/by-id/<int:agent_id>',
            resource_class_args=[service_proxy],
        )

        api.add_resource(
            AgentByNumber,
            '/agents/by-number/<agent_number>',
            resource_class_args=[service_proxy],
        )

        api.add_resource(
            UserAgent,
            '/users/me/agents',
            resource_class_args=[service_proxy],
        )

        api.add_resource(
            UserQueues,
            '/users/me/agents/queues',
            resource_class_args=[service_proxy],
        )

        api.add_resource(
            AgentQueuesById,
            '/agents/by-id/<int:agent_id>/queues',
            resource_class_args=[service_proxy],
        )

        api.add_resource(
            AgentQueuesByNumber,
            '/agents/by-number/<agent_number>/queues',
            resource_class_args=[service_proxy],
        )

        api.add_resource(
            LoginAgentById,
            '/agents/by-id/<int:agent_id>/login',
            resource_class_args=[service_proxy],
        )

        api.add_resource(
            LoginAgentByNumber,
            '/agents/by-number/<agent_number>/login',
            resource_class_args=[service_proxy],
        )

        api.add_resource(
            LoginUserAgent,
            '/users/me/agents/login',
            resource_class_args=[service_proxy],
        )

        api.add_resource(
            LogoffAgentById,
            '/agents/by-id/<int:agent_id>/logoff',
            resource_class_args=[service_proxy],
        )

        api.add_resource(
            LogoffAgentByNumber,
            '/agents/by-number/<agent_number>/logoff',
            resource_class_args=[service_proxy],
        )

        api.add_resource(
            LogoffUserAgent,
            '/users/me/agents/logoff',
            resource_class_args=[service_proxy],
        )

        api.add_resource(
            PauseUserAgent,
            '/users/me/agents/pause',
            resource_class_args=[service_proxy],
        )

        api.add_resource(
            UnpauseUserAgent,
            '/users/me/agents/unpause',
            resource_class_args=[service_proxy],
        )

        api.add_resource(
            AddAgentToQueue,
            '/agents/by-id/<int:agent_id>/add',
            resource_class_args=[service_proxy],
        )

        api.add_resource(
            RemoveAgentFromQueue,
            '/agents/by-id/<int:agent_id>/remove',
            resource_class_args=[service_proxy],
        )

        api.add_resource(
            PauseAgentByNumber,
            '/agents/by-number/<agent_number>/pause',
            resource_class_args=[service_proxy],
        )

        api.add_resource(
            UnpauseAgentByNumber,
            '/agents/by-number/<agent_number>/unpause',
            resource_class_args=[service_proxy],
        )
