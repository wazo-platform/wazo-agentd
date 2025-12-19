# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from xivo_dao.helpers import db_utils

if TYPE_CHECKING:
    from xivo_dao import agent_status_dao as AgentStatusDAO
    from xivo_dao.agent_dao import _Agent as Agent

    from wazo_agentd.dao import _Queue as Queue
    from wazo_agentd.service.action.add import AddToQueueAction

logger = logging.getLogger(__name__)


class OnQueueMemberAssociatedManager:
    def __init__(
        self, add_to_queue_action: AddToQueueAction, agent_status_dao: AgentStatusDAO
    ):
        self._add_to_queue = add_to_queue_action.add_agent_to_queue
        self._agent_status_dao = agent_status_dao

    def on_queue_member_associated(self, agent: Agent, queue: Queue, penalty: int):
        if agent.tenant_uuid != queue.tenant_uuid:
            logger.warning(
                'agent %s and queue %s are not in the same tenant', agent.id, queue.id
            )
            return

        with db_utils.session_scope():
            if not (agent_status := self._agent_status_dao.get_status(agent.id)):
                return

        if queue.penalty != penalty:
            queue = queue._replace(penalty=penalty)

        self._add_to_queue(agent_status, queue)
