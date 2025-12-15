# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, TypeAlias

from wazo_bus.resources.user_agent.event import UserAgentQueueLoggedOffEvent

from wazo_agentd.exception import (
    AgentNotLoggedError,
    NoSuchQueueError,
    QueueDifferentTenantError,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from xivo_dao import agent_status_dao as AgentStatusDAO
    from xivo_dao.resources.user import dao as UserDAO

    from wazo_agentd.bus import BusPublisher
    from wazo_agentd.dao import _Queue as Queue
    from wazo_agentd.service.action.remove import RemoveFromQueueAction

    AgentStatus: TypeAlias = AgentStatusDAO._AgentStatus


@dataclass
class _ActionsContainer:
    remove_agent_from_queue: Callable[[AgentStatus, Queue], None]


class QueueLogoffManager:
    _actions: _ActionsContainer
    _bus_publisher: BusPublisher

    def __init__(
        self,
        remove_from_queue_action: RemoveFromQueueAction,
        user_dao: UserDAO,
        bus_publisher: BusPublisher,
    ):
        self._actions = _ActionsContainer(
            remove_from_queue_action.remove_agent_from_queue
        )
        self._user_dao = user_dao
        self._bus_publisher = bus_publisher

    def _is_already_logged_in_queue(
        self, agent_status: AgentStatus, queue: Queue
    ) -> bool:
        for agent_queue in agent_status.queues:
            if agent_queue.name == queue.name:
                return agent_queue.logged
        raise NoSuchQueueError()

    def _send_bus_event(self, agent_status: AgentStatus, queue: Queue) -> None:
        tenant_uuid = agent_status.tenant_uuid
        user_uuids = [
            u.uuid for u in self._user_dao.find_all_by_agent_id(agent_status.agent_id)
        ]

        event = UserAgentQueueLoggedOffEvent(
            agent_status.agent_id, queue.id, tenant_uuid, user_uuids
        )
        self._bus_publisher.publish(event)

    def logoff_from_queue(self, agent_status: AgentStatus | None, queue: Queue) -> None:
        if not agent_status:
            raise AgentNotLoggedError()

        if agent_status.tenant_uuid != queue.tenant_uuid:
            raise QueueDifferentTenantError()

        if self._is_already_logged_in_queue(agent_status, queue):
            self._actions.remove_agent_from_queue(agent_status, queue)
            self._send_bus_event(agent_status, queue)
