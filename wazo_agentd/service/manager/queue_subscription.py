# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from wazo_bus.resources.user_agent.event import (
    UserAgentQueueSubscribedEvent,
    UserAgentQueueUnsubscribedEvent,
)
from xivo_dao.helpers import db_utils

from wazo_agentd.exception import (
    AgentNotLoggedError,
    NoSuchQueueError,
    QueueDifferentTenantError,
)

if TYPE_CHECKING:
    from xivo_dao import agent_status_dao as AgentStatusDAO
    from xivo_dao.resources.user import dao as UserDAO

    from wazo_agentd.bus import BusPublisher
    from wazo_agentd.service.action.add import AddToQueueAction
    from wazo_agentd.service.action.remove import RemoveFromQueueAction


@dataclass
class _ActionsContainer:
    add: AddToQueueAction
    remove: RemoveFromQueueAction


@dataclass
class _DAOContainer:
    agent_status: AgentStatusDAO
    user: UserDAO


class QueueSubscriptionManager:
    _actions: _ActionsContainer
    _bus_publisher: BusPublisher
    _dao: _DAOContainer

    def __init__(
        self,
        add_to_queue_action: AddToQueueAction,
        remove_from_queue_action: RemoveFromQueueAction,
        agent_status_dao: AgentStatusDAO,
        user_dao: UserDAO,
        bus_publisher: BusPublisher,
    ):
        self._actions = _ActionsContainer(add_to_queue_action, remove_from_queue_action)
        self._dao = _DAOContainer(agent_status_dao, user_dao)
        self._bus_publisher = bus_publisher

    def queue_subscribe(self, agent, queue) -> None:
        self._assert_same_tenant(agent, queue)
        agent_status = self._get_agent_status(agent)

        if not self._is_subscribed_to_queue(agent_status, queue):
            self._actions.add.add_agent_to_queue(agent_status, queue)
            self._send_bus_subscribe_event(agent, queue)

    def queue_unsubscribe(self, agent, queue) -> None:
        self._assert_same_tenant(agent, queue)
        agent_status = self._get_agent_status(agent)

        if self._is_subscribed_to_queue(agent_status, queue):
            self._actions.remove.remove_agent_from_queue(agent_status, queue)
            self._send_bus_unsubscribe_event(agent, queue)

    def _assert_same_tenant(self, agent, queue) -> None:
        if agent.tenant_uuid != queue.tenant_uuid:
            raise QueueDifferentTenantError()

    def _is_subscribed_to_queue(self, agent, queue) -> bool:
        if agent is None:
            raise AgentNotLoggedError()

        for agent_queue in agent.queues:
            if agent_queue.name == queue.name:
                return agent_queue.logged
        raise NoSuchQueueError()

    def _get_agent_status(self, agent) -> dict | None:
        with db_utils.session_scope():
            return self._dao.agent_status.get_status(agent.id)

    def _get_agent_users(self, agent) -> list[str]:
        with db_utils.session_scope():
            return [user.uuid for user in self._dao.user.find_all_by_agent_id(agent.id)]

    def _send_bus_subscribe_event(self, agent, queue) -> None:
        tenant_uuid = agent.tenant_uuid
        user_uuids = self._get_agent_users(agent)

        self._bus_publisher.publish(
            UserAgentQueueSubscribedEvent(agent.id, queue.id, tenant_uuid, user_uuids)
        )

    def _send_bus_unsubscribe_event(self, agent, queue) -> None:
        tenant_uuid = agent.tenant_uuid
        user_uuids = self._get_agent_users(agent)

        self._bus_publisher.publish(
            UserAgentQueueUnsubscribedEvent(agent.id, queue.id, tenant_uuid, user_uuids)
        )
