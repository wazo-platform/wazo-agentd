# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from typing import TYPE_CHECKING, TypeAlias

if TYPE_CHECKING:
    from xivo_dao import agent_status_dao as AgentStatusDAO

    from wazo_agentd.dao import _Queue as Queue
    from wazo_agentd.service.action.add import AddToQueueAction

    AgentStatus: TypeAlias = AgentStatusDAO._AgentStatus


class OnQueueMemberAssociatedManager:
    def __init__(self, add_to_queue_action: AddToQueueAction):
        self._add_to_queue = add_to_queue_action.add_agent_to_queue

    def on_queue_member_associated(
        self, agent_status: AgentStatus | None, queue: Queue, penalty: int
    ):
        if not agent_status:
            return

        if queue.penalty != penalty:
            queue = queue._replace(penalty=penalty)

        self._add_to_queue(agent_status, queue)
