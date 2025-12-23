# Copyright 2013-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from typing import TYPE_CHECKING, TypeAlias

from xivo_dao.helpers import db_utils

if TYPE_CHECKING:
    from xivo_dao import agent_status_dao as AgentStatusDAO
    from xivo_dao.agent_dao import _Agent as Agent

    from wazo_agentd.dao import _Queue as Queue
    from wazo_agentd.service.action.update import UpdatePenaltyAction

    QueueStatus: TypeAlias = AgentStatusDAO._Queue
    AgentStatus: TypeAlias = AgentStatusDAO._AgentStatus


class OnAgentUpdatedManager:
    def __init__(
        self,
        update_penalty_action: UpdatePenaltyAction,
        agent_status_dao: AgentStatusDAO,
    ):
        self._update_penalty = update_penalty_action.update
        self._agent_status_dao = agent_status_dao

    def on_agent_updated(self, agent: Agent):
        with db_utils.session_scope(read_only=True):
            if not (agent_status := self._agent_status_dao.get_status(agent.id)):
                return

        self._update_queues_penalty(agent_status, agent)

    def _update_queues_penalty(self, agent_status: AgentStatus, agent: Agent):
        updated_queues: dict[int, Queue] = {q.id: q for q in agent.queues}
        previous_queues: dict[int, QueueStatus] = {q.id: q for q in agent_status.queues}

        for key in previous_queues.keys():
            queue = previous_queues[key]
            if not (updated := updated_queues.get(key)):
                continue

            if queue.penalty != updated.penalty:
                queue = queue._replace(penalty=updated.penalty)
                self._update_penalty(agent_status, queue)
