# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from xivo import debug
from xivo_dao.helpers import db_utils

logger = logging.getLogger(__name__)


class AgentQueuesHandler:
    def __init__(self, agent_dao):
        self._agent_dao = agent_dao

    @debug.trace_duration
    def handle_list_user_queues(self, user_uuid, tenant_uuids=None):
        logger.info('Executing list_user_queues command (user %s)', user_uuid)
        with db_utils.session_scope():
            agent = self._agent_dao.get_agent_by_user_uuid(
                user_uuid, tenant_uuids=tenant_uuids
            )
        return self._handle_list_user_queues(agent)

    @debug.trace_duration
    def handle_list_queues_by_id(self, agent_id, tenant_uuids=None):
        logger.info('Executing list_queues_by_id command (agent %s)', agent_id)
        with db_utils.session_scope():
            agent = self._agent_dao.get_agent(agent_id, tenant_uuids=tenant_uuids)
        return self._handle_list_user_queues(agent)

    def _handle_list_user_queues(self, agent):
        return [
            {
                'id': queue.id,
                'name': queue.name,
                'display_name': queue.label,
            }
            for queue in agent.queues
        ]
