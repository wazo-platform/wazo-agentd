# Copyright 2013-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from typing import TYPE_CHECKING

from xivo_dao.helpers import db_utils

if TYPE_CHECKING:
    from xivo_dao import agent_status_dao as AgentStatusDAO

    from wazo_agentd.dao import _Queue as Queue
    from wazo_agentd.service.action.add import AddToQueueAction


class OnQueueAddedManager:
    def __init__(
        self, add_to_queue_action: AddToQueueAction, agent_status_dao: AgentStatusDAO
    ):
        self._add_to_queue_action = add_to_queue_action
        self._agent_status_dao = agent_status_dao

    def on_queue_added(self, queue: Queue):
        with db_utils.session_scope():
            agent_statuses = self._agent_status_dao.get_statuses_for_queue(queue.id)

        for agent_status in agent_statuses:
            self._add_to_queue_action.add_agent_to_queue_by_status(agent_status, queue)
