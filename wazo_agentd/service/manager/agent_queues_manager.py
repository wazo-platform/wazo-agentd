# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from xivo_dao.helpers import db_utils

from wazo_agentd.exception import (
    AgentNotLoggedError,
    NoSuchQueueError,
    QueueDifferentTenantError,
)

if TYPE_CHECKING:
    from xivo_dao import agent_status_dao as AgentStatusDAO

    from wazo_agentd.service.action.add import AddToQueueAction
    from wazo_agentd.service.action.remove import RemoveFromQueueAction


@dataclass
class _Actions:
    add: AddToQueueAction
    remove: RemoveFromQueueAction


class AgentQueuesManager:
    _agent_status_dao: AgentStatusDAO
    _actions: _Actions

    def __init__(
        self,
        add_to_queue_action: AddToQueueAction,
        remove_from_queue_action: RemoveFromQueueAction,
        agent_status_dao: AgentStatusDAO,
    ):
        self._actions = _Actions(add_to_queue_action, remove_from_queue_action)
        self._agent_status_dao = agent_status_dao

    def queue_subscribe(self, agent, queue) -> None:
        self._assert_same_tenant(agent, queue)
        agent_status = self._get_agent_status(agent)

        if not self._is_subscribed_to_queue(agent_status, queue):
            self._actions.add.add_agent_to_queue(agent_status, queue)

    def queue_unsubscribe(self, agent, queue) -> None:
        self._assert_same_tenant(agent, queue)
        agent_status = self._get_agent_status(agent)

        if self._is_subscribed_to_queue(agent_status, queue):
            self._actions.remove.remove_agent_from_queue(agent_status, queue)

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
            return self._agent_status_dao.get_status(agent.id)
