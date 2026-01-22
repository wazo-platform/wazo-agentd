# Copyright 2013-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from typing import TYPE_CHECKING, TypeAlias

from xivo_dao.helpers import db_utils

if TYPE_CHECKING:
    from collections.abc import Iterable

    from xivo_dao import agent_status_dao as AgentStatusDAO

    from wazo_agentd.dao import _Queue as Queue
    from wazo_agentd.service.action.add import AddToQueueAction
    from wazo_agentd.service.action.remove import RemoveFromQueueAction

    AgentStatus: TypeAlias = AgentStatusDAO._AgentStatus


class OnQueueUpdatedManager:
    def __init__(
        self,
        add_to_queue_action: AddToQueueAction,
        remove_from_queue_action: RemoveFromQueueAction,
        agent_status_dao: AgentStatusDAO,
    ):
        self._add_to_queue_action = add_to_queue_action
        self._remove_from_queue_action = remove_from_queue_action
        self._agent_status_dao = agent_status_dao

    def on_queue_updated(self, queue: Queue):
        with db_utils.session_scope():
            added_agent_statuses = self._agent_status_dao.get_statuses_to_add_to_queue(
                queue.id
            )
            removed_agent_statuses = (
                self._agent_status_dao.get_statuses_to_remove_from_queue(queue.id)
            )

        self._manage_added_agents(added_agent_statuses, queue)
        self._manage_removed_agents(removed_agent_statuses, queue)

    def _manage_added_agents(self, agent_statuses: Iterable[AgentStatus], queue: Queue):
        for agent_status in agent_statuses:
            self._add_to_queue_action.add_agent_to_queue_by_status(agent_status, queue)

    def _manage_removed_agents(
        self, agent_statuses: Iterable[AgentStatus], queue: Queue
    ):
        for agent_status in agent_statuses:
            self._remove_from_queue_action.remove_agent_from_queue_by_status(
                agent_status, queue
            )
