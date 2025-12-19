# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from xivo import debug
from xivo_dao.helpers import db_utils

if TYPE_CHECKING:
    from xivo_dao import agent_status_dao as AgentStatusDAO

    from wazo_agentd.dao import QueueDAOAdapter as QueueDAO
    from wazo_agentd.service.manager.on_queue_member_associated import (
        OnQueueMemberAssociatedManager,
    )
    from wazo_agentd.service.manager.on_queue_member_dissociated import (
        OnQueueMemberDissociatedManager,
    )

logger = logging.getLogger(__name__)


class OnQueueMemberHandler:
    def __init__(
        self,
        association_manager: OnQueueMemberAssociatedManager,
        dissociation_manager: OnQueueMemberDissociatedManager,
        agent_status_dao: AgentStatusDAO,
        queue_dao: QueueDAO,
    ):
        self._association_manager = association_manager
        self._dissociation_manager = dissociation_manager
        self._agent_status_dao = agent_status_dao
        self._queue_dao = queue_dao

    @debug.trace_duration
    def handle_on_queue_member_agent_associated(
        self, agent_id: int, queue_id: int, penalty: int
    ):
        logger.info(
            'Executing on queue agent associated (agent ID %s, queue ID %s)',
            agent_id,
            queue_id,
        )
        with db_utils.session_scope():
            agent_status = self._agent_status_dao.get_status(agent_id)
            queue = self._queue_dao.get_queue(queue_id)

        self._association_manager.on_queue_member_associated(
            agent_status, queue, penalty
        )

    @debug.trace_duration
    def handle_on_queue_member_agent_dissociated(self, agent_id: int, queue_id: int):
        logger.info(
            'Executing on queue agent dissociated (agent ID %s, queue ID %s)',
            agent_id,
            queue_id,
        )
        with db_utils.session_scope():
            agent_status = self._agent_status_dao.get_status(agent_id)
            queue = self._queue_dao.get_queue(queue_id)

        self._dissociation_manager.on_queue_member_dissociated(agent_status, queue)
