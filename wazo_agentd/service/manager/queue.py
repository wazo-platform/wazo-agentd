# Copyright 2025-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from typing import TYPE_CHECKING, TypeAlias

from wazo_bus.resources.user_agent.event import (
    UserAgentQueueLoggedInEvent,
    UserAgentQueueLoggedOffEvent,
)
from xivo_dao.helpers import db_utils

from wazo_agentd.exception import (
    AgentNotLoggedError,
    NoSuchQueueError,
    QueueDifferentTenantError,
)

if TYPE_CHECKING:
    from xivo_dao import agent_dao as AgentDAO
    from xivo_dao import agent_status_dao as AgentStatusDAO
    from xivo_dao.resources.user import dao as UserDAO

    from wazo_agentd.bus import BusPublisher
    from wazo_agentd.dao import _Queue as Queue
    from wazo_agentd.service.action.add import AddToQueueAction
    from wazo_agentd.service.action.remove import RemoveFromQueueAction

    Agent: TypeAlias = AgentDAO._Agent
    AgentStatus: TypeAlias = AgentStatusDAO._AgentStatus
    QueueStatus: TypeAlias = AgentStatusDAO._Queue


class QueueManager:
    def __init__(
        self,
        add_to_queue_action: AddToQueueAction,
        remove_from_queue_action: RemoveFromQueueAction,
        agent_status_dao: AgentStatusDAO,
        user_dao: UserDAO,
        bus_publisher: BusPublisher,
    ):
        self._add_to_queue_action = add_to_queue_action
        self._remove_from_queue_action = remove_from_queue_action
        self._agent_status_dao = agent_status_dao
        self._user_dao = user_dao
        self._bus_publisher = bus_publisher

    def _get_agent_users_uuids(self, agent: Agent) -> list[str]:
        with db_utils.session_scope():
            return [u.uuid for u in self._user_dao.find_all_by_agent_id(agent.id)]

    def _get_agent_queue(self, agent_status: AgentStatus, queue: Queue) -> QueueStatus:
        for agent_queue in agent_status.queues:
            if agent_queue.name == queue.name:
                return agent_queue
        raise NoSuchQueueError()

    def _send_bus_event(
        self,
        event_cls: (
            type[UserAgentQueueLoggedInEvent] | type[UserAgentQueueLoggedOffEvent]
        ),
        agent: Agent,
        queue: QueueStatus,
    ) -> None:
        tenant_uuid = agent.tenant_uuid
        user_uuids = self._get_agent_users_uuids(agent)

        event = event_cls(agent.id, queue.id, tenant_uuid, user_uuids)
        self._bus_publisher.publish(event)

    def login_to_queue(self, agent: Agent, queue: Queue) -> None:
        with db_utils.session_scope():
            agent_status = self._agent_status_dao.get_status(agent.id)

        if not agent_status:
            raise AgentNotLoggedError()

        if agent.tenant_uuid != queue.tenant_uuid:
            raise QueueDifferentTenantError()

        agent_queue = self._get_agent_queue(agent_status, queue)

        # NOTE: Since queue from wazo_agentd.dao penalty is hardcoded to 0, we must update it
        queue = queue._replace(penalty=agent_queue.penalty)

        if not agent_queue.logged:
            self._add_to_queue_action.add_agent_to_queue_by_status(agent_status, queue)
            self._send_bus_event(UserAgentQueueLoggedInEvent, agent, agent_queue)

    def logoff_from_queue(self, agent: Agent, queue: Queue) -> None:
        with db_utils.session_scope():
            agent_status = self._agent_status_dao.get_status(agent.id)

        if not agent_status:
            raise AgentNotLoggedError()

        if agent.tenant_uuid != queue.tenant_uuid:
            raise QueueDifferentTenantError()

        agent_queue = self._get_agent_queue(agent_status, queue)

        if agent_queue.logged:
            self._remove_from_queue_action.remove_agent_from_queue_by_status(
                agent_status, agent_queue
            )
            self._send_bus_event(UserAgentQueueLoggedOffEvent, agent, agent_queue)
