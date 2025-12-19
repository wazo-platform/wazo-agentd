# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from typing import TYPE_CHECKING, TypeAlias

if TYPE_CHECKING:
    from xivo_dao import agent_status_dao as AgentStatusDAO

    from wazo_agentd.dao import _Queue as Queue
    from wazo_agentd.service.action.remove import RemoveFromQueueAction

    AgentStatus: TypeAlias = AgentStatusDAO._AgentStatus


class OnQueueMemberDissociatedManager:
    def __init__(self, remove_from_queue_action: RemoveFromQueueAction):
        self._remove_from_queue = remove_from_queue_action.remove_agent_from_queue

    def on_queue_member_dissociated(
        self, agent_status: AgentStatus | None, queue: Queue
    ):
        if not agent_status:
            return

        self._remove_from_queue(agent_status, queue)
