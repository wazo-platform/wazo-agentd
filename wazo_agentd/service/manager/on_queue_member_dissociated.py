# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, TypeAlias

from xivo_dao.helpers import db_utils

if TYPE_CHECKING:
    from xivo_dao import agent_status_dao as AgentStatusDAO
    from xivo_dao.agent_dao import _Agent as Agent

    from wazo_agentd.dao import _Queue as Queue
    from wazo_agentd.service.action.remove import RemoveFromQueueAction

    AgentStatus: TypeAlias = AgentStatusDAO._AgentStatus

logger = logging.getLogger(__name__)


class OnQueueMemberDissociatedManager:
    def __init__(
        self,
        remove_from_queue_action: RemoveFromQueueAction,
        agent_status_dao: AgentStatusDAO,
    ):
        self._remove_from_queue = remove_from_queue_action.remove_agent_from_queue
        self._agent_status_dao = agent_status_dao

    def on_queue_member_dissociated(self, agent: Agent, queue: Queue):
        if agent.tenant_uuid != queue.tenant_uuid:
            logger.warning(
                'agent %s and queue %s are not in the same tenant', agent.id, queue.id
            )
            return

        with db_utils.session_scope():
            if not (agent_status := self._agent_status_dao.get_status(agent.id)):
                return

        self._remove_from_queue(agent_status, queue)
