# Copyright 2025-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from xivo_dao.agent_dao import _Agent as Agent

    from wazo_agentd.dao import _Queue as Queue
    from wazo_agentd.service.action.add import AddToQueueAction

logger = logging.getLogger(__name__)


class OnQueueMemberAssociatedManager:
    def __init__(self, add_to_queue_action: AddToQueueAction):
        self._add_to_queue_action = add_to_queue_action

    def on_queue_member_associated(self, agent: Agent, queue: Queue, penalty: int):
        if agent.tenant_uuid != queue.tenant_uuid:
            logger.warning(
                'agent %s and queue %s are not in the same tenant', agent.id, queue.id
            )
            return

        if queue.penalty != penalty:
            queue = queue._replace(penalty=penalty)

        self._add_to_queue_action.add_agent_to_queue(agent, queue)
