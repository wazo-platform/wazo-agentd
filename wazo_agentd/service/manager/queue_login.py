# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, TypeAlias

from wazo_bus.resources.user_agent.event import UserAgentQueueLoggedInEvent
from xivo_dao.helpers import db_utils

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
    from wazo_agentd.service.action.add import AddToQueueAction

    AgentStatus: TypeAlias = AgentStatusDAO._AgentStatus


@dataclass
class _ActionsContainer:
    add_agent_to_queue: Callable[[AgentStatus, Queue], None]


class QueueLoginManager:
    _actions: _ActionsContainer
    _bus_publisher: BusPublisher

    def __init__(
        self,
        add_to_queue_action: AddToQueueAction,
        user_dao: UserDAO,
        bus_publisher: BusPublisher,
    ):
        self._actions = _ActionsContainer(add_to_queue_action.add_agent_to_queue)
        self._user_dao = user_dao
        self._bus_publisher = bus_publisher

    def _get_agent_users_uuids(self, agent_status: AgentStatus) -> list[str]:
        agent_id = agent_status.agent_id
        with db_utils.session_scope():
            return [u.uuid for u in self._user_dao.find_all_by_agent_id(agent_id)]

    def _is_already_logged_in_queue(
        self, agent_status: AgentStatus, queue: Queue
    ) -> bool:
        for agent_queue in agent_status.queues:
            if agent_queue.name == queue.name:
                return agent_queue.logged
        raise NoSuchQueueError()

    def _send_bus_event(self, agent_status: AgentStatus, queue: Queue) -> None:
        tenant_uuid = agent_status.tenant_uuid
        user_uuids = self._get_agent_users_uuids(agent_status)

        event = UserAgentQueueLoggedInEvent(
            agent_status.agent_id, queue.id, tenant_uuid, user_uuids
        )
        self._bus_publisher.publish(event)

    def login_to_queue(self, agent_status: AgentStatus | None, queue: Queue) -> None:
        if not agent_status:
            raise AgentNotLoggedError()

        if agent_status.tenant_uuid != queue.tenant_uuid:
            raise QueueDifferentTenantError()

        if not self._is_already_logged_in_queue(agent_status, queue):
            self._actions.add_agent_to_queue(agent_status, queue)
            self._send_bus_event(agent_status, queue)
