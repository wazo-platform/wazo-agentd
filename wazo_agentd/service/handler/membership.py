# Copyright 2013-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import logging

from typing import TYPE_CHECKING

from xivo import debug
from xivo_dao.helpers import db_utils

if TYPE_CHECKING:
    from wazo_agentd.dao import AgentDAOAdapter
    from wazo_agentd.service.manager.agent_queues_manager import AgentQueuesManager

logger = logging.getLogger(__name__)


class MembershipHandler:
    _agent_queues_manager: AgentQueuesManager
    _agent_dao: AgentDAOAdapter

    def __init__(
        self,
        add_member_manager,
        remove_member_manager,
        agent_queues_manager,
        agent_dao,
        queue_dao,
    ):
        self._add_member_manager = add_member_manager
        self._remove_member_manager = remove_member_manager
        self._agent_queues_manager = agent_queues_manager
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
    def handle_subscribe_user_agent_to_queue(
        self, user_uuid, queue_id, tenant_uuids=None
    ):
        with db_utils.session_scope():
            agent = self._agent_dao.get_agent_by_user_uuid(user_uuid, tenant_uuids)
            queue = self._queue_dao.get_queue(queue_id, tenant_uuids=tenant_uuids)
        self._agent_queues_manager.queue_subscribe(agent, queue)

    @debug.trace_duration
    def handle_unsubscribe_user_agent_from_queue(
        self, user_uuid, queue_id, tenant_uuids=None
    ):
        with db_utils.session_scope():
            agent = self._agent_dao.get_agent_by_user_uuid(user_uuid, tenant_uuids)
            queue = self._queue_dao.get_queue(queue_id, tenant_uuids=tenant_uuids)
        self._agent_queues_manager.queue_unsubscribe(agent, queue)
