# Copyright 2013-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from xivo import debug
from xivo_dao.helpers import db_utils

if TYPE_CHECKING:
    from wazo_agentd.dao import AgentDAOAdapter as AgentDAO
    from wazo_agentd.dao import QueueDAOAdapter as QueueDAO
    from wazo_agentd.service.manager.add_member import AddMemberManager
    from wazo_agentd.service.manager.queue import QueueManager
    from wazo_agentd.service.manager.remove_member import RemoveMemberManager

logger = logging.getLogger(__name__)


class MembershipHandler:
    def __init__(
        self,
        add_member_manager: AddMemberManager,
        remove_member_manager: RemoveMemberManager,
        queue_manager: QueueManager,
        agent_dao: AgentDAO,
        queue_dao: QueueDAO,
    ):
        self._add_member_manager = add_member_manager
        self._remove_member_manager = remove_member_manager
        self._queue_manager = queue_manager
        self._agent_dao = agent_dao
        self._queue_dao = queue_dao

    @debug.trace_duration
    def handle_add_to_queue(self, agent_id, queue_id, tenant_uuids=None):
        logger.info(
            'Executing add to queue command (agent ID %s, queue ID %s)',
            agent_id,
            queue_id,
        )
        with db_utils.session_scope():
            agent = self._agent_dao.get_agent(agent_id, tenant_uuids=tenant_uuids)
            queue = self._queue_dao.get_queue(queue_id, tenant_uuids=tenant_uuids)
        self._add_member_manager.add_agent_to_queue(agent, queue)

    @debug.trace_duration
    def handle_remove_from_queue(self, agent_id, queue_id, tenant_uuids=None):
        logger.info(
            'Executing remove from queue command (agent ID %s, queue ID %s)',
            agent_id,
            queue_id,
        )
        with db_utils.session_scope():
            agent = self._agent_dao.get_agent(agent_id, tenant_uuids=tenant_uuids)
            queue = self._queue_dao.get_queue(queue_id, tenant_uuids=tenant_uuids)
        self._remove_member_manager.remove_agent_from_queue(agent, queue)

    @debug.trace_duration
    def handle_user_agent_queue_login(self, user_uuid, queue_id, tenant_uuids=None):
        logger.info(
            'Executing queue login command (agent of user %s, queue ID %s)',
            user_uuid,
            queue_id,
        )
        with db_utils.session_scope():
            agent = self._agent_dao.get_agent_by_user_uuid(user_uuid, tenant_uuids)
            queue = self._queue_dao.get_queue(queue_id, tenant_uuids)
        self._queue_manager.login_to_queue(agent, queue)

    @debug.trace_duration
    def handle_user_agent_queue_logoff(self, user_uuid, queue_id, tenant_uuids=None):
        logger.info(
            'Executing queue logoff command (agent of user %s, queue ID %s)',
            user_uuid,
            queue_id,
        )
        with db_utils.session_scope():
            agent = self._agent_dao.get_agent_by_user_uuid(user_uuid, tenant_uuids)
            queue = self._queue_dao.get_queue(queue_id, tenant_uuids)
        self._queue_manager.logoff_from_queue(agent, queue)
