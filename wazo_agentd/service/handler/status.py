# Copyright 2013-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from xivo import debug
from xivo_dao.helpers import db_utils

logger = logging.getLogger(__name__)


class StatusHandler:
    def __init__(self, agent_dao, agent_status_dao, uuid):
        self._agent_dao = agent_dao
        self._agent_status_dao = agent_status_dao
        self._uuid = uuid

    @debug.trace_duration
    def handle_status_by_id(self, agent_id, tenant_uuids=None):
        logger.info('Executing status command (ID %s)', agent_id)
        with db_utils.session_scope():
            agent = self._agent_dao.get_agent(agent_id, tenant_uuids=tenant_uuids)
        return self._handle_status(agent)

    @debug.trace_duration
    def handle_status_by_number(self, agent_number, tenant_uuids=None):
        logger.info('Executing status command (number %s)', agent_number)
        with db_utils.session_scope():
            agent = self._agent_dao.get_agent_by_number(
                agent_number, tenant_uuids=tenant_uuids
            )
        return self._handle_status(agent)

    @debug.trace_duration
    def handle_status_by_user(self, user_uuid, tenant_uuids=None):
        logger.info('Executing status command (agent of user %s)', user_uuid)
        with db_utils.session_scope():
            agent = self._agent_dao.get_agent_by_user_uuid(
                user_uuid, tenant_uuids=tenant_uuids
            )
        return self._handle_status(agent)

    @debug.trace_duration
    def handle_statuses(self, tenant_uuids=None):
        logger.info('Executing statuses command')
        with db_utils.session_scope():
            agent_statuses = self._agent_status_dao.get_statuses(
                tenant_uuids=tenant_uuids
            )
            return [
                {
                    'id': status.agent_id,
                    'tenant_uuid': status.tenant_uuid,
                    'origin_uuid': self._uuid,
                    'number': status.agent_number,
                    'logged': status.logged,
                    'paused': status.paused,
                    'paused_reason': status.paused_reason,
                    'extension': status.extension,
                    'context': status.context,
                    'state_interface': status.state_interface,
                    'queues': [
                        {
                            'id': queue.id,
                            'name': queue.name,
                            'display_name': queue.display_name,
                            'logged': queue.logged,
                            'paused': queue.paused,
                            'paused_reason': queue.paused_reason,
                        }
                        for queue in status.queues
                    ],
                }
                for status in agent_statuses
            ]

    def _handle_status(self, agent):
        with db_utils.session_scope():
            agent_status = self._agent_status_dao.get_status(agent.id)
            if agent_status is None:
                logged = False
                paused = False
                paused_reason = None
                extension = None
                context = None
                state_interface = None
                queues = []
            else:
                logged = True
                paused = agent_status.paused
                paused_reason = agent_status.paused_reason
                extension = agent_status.extension
                context = agent_status.context
                state_interface = agent_status.state_interface
                queues = agent_status.queues
            return {
                'id': agent.id,
                'tenant_uuid': agent.tenant_uuid,
                'origin_uuid': self._uuid,
                'number': agent.number,
                'logged': logged,
                'paused': paused,
                'paused_reason': paused_reason,
                'extension': extension,
                'context': context,
                'state_interface': state_interface,
                'queues': [
                    {
                        'id': queue.id,
                        'name': queue.name,
                        'display_name': queue.display_name,
                        'logged': queue.logged,
                        'paused': queue.paused,
                        'paused_reason': queue.paused_reason,
                    }
                    for queue in queues
                ],
            }
