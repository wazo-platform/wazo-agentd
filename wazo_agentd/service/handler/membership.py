# Copyright 2013-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from xivo import debug
from xivo_dao.helpers import db_utils

if TYPE_CHECKING:
    from xivo_dao import agent_status_dao as AgentStatusDAO

    from wazo_agentd.dao import AgentDAOAdapter, QueueDAOAdapter
    from wazo_agentd.service.manager.queue_login import QueueLoginManager
    from wazo_agentd.service.manager.queue_logoff import QueueLogoffManager

logger = logging.getLogger(__name__)


class MembershipHandler:
    _agent_dao: AgentDAOAdapter
    _agent_status_dao: AgentStatusDAO
    _queue_dao: QueueDAOAdapter
    _queue_login_manager: QueueLoginManager
    _queue_logoff_manager: QueueLogoffManager

    def __init__(
        self,
        add_member_manager,
        remove_member_manager,
        queue_login_manager,
        queue_logoff_manager,
        agent_dao,
        agent_status_dao,
        queue_dao,
    ):
        self._add_member_manager = add_member_manager
        self._remove_member_manager = remove_member_manager
        self._queue_login_manager = queue_login_manager
        self._queue_logoff_manager = queue_logoff_manager
        self._agent_dao = agent_dao
        self._agent_status_dao = agent_status_dao
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
            self._agent_dao.get_agent_by_user_uuid(user_uuid, tenant_uuids)
            status = self._agent_status_dao.get_status_by_user(user_uuid, tenant_uuids)
            queue = self._queue_dao.get_queue(queue_id, tenant_uuids)
        self._queue_login_manager.login_to_queue(status, queue)

    @debug.trace_duration
    def handle_user_agent_queue_logoff(self, user_uuid, queue_id, tenant_uuids=None):
        logger.info(
            'Executing queue logoff command (agent of user %s, queue ID %s)',
            user_uuid,
            queue_id,
        )
        with db_utils.session_scope():
            self._agent_dao.get_agent_by_user_uuid(user_uuid, tenant_uuids)
            status = self._agent_status_dao.get_status_by_user(user_uuid, tenant_uuids)
            queue = self._queue_dao.get_queue(queue_id, tenant_uuids)
        self._queue_logoff_manager.logoff_from_queue(status, queue)
