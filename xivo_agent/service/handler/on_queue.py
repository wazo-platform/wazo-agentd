# -*- coding: utf-8 -*-
# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import logging

from xivo import debug
from xivo_dao.helpers import db_utils

logger = logging.getLogger(__name__)


class OnQueueHandler(object):

    def __init__(self, on_queue_added_manager, on_queue_updated_manager, on_queue_deleted_manager,
                 on_queue_agent_paused_manager, on_queue_agent_call_manager, queue_dao, agent_dao):
        self._on_queue_added_manager = on_queue_added_manager
        self._on_queue_updated_manager = on_queue_updated_manager
        self._on_queue_deleted_manager = on_queue_deleted_manager
        self._on_queue_agent_paused_manager = on_queue_agent_paused_manager
        self._on_queue_agent_call_manager = on_queue_agent_call_manager 
        self._queue_dao = queue_dao
        self._agent_dao = agent_dao

    @debug.trace_duration
    def handle_on_queue_added(self, queue_id):
        logger.info('Executing on queue added command (ID %s)', queue_id)
        with db_utils.session_scope():
            queue = self._queue_dao.get_queue(queue_id)
        self._on_queue_added_manager.on_queue_added(queue)

    @debug.trace_duration
    def handle_on_queue_updated(self, queue_id):
        logger.info('Executing on queue updated command (ID %s)', queue_id)
        with db_utils.session_scope():
            queue = self._queue_dao.get_queue(queue_id)
        self._on_queue_updated_manager.on_queue_updated(queue)

    @debug.trace_duration
    def handle_on_queue_deleted(self, queue_id):
        logger.info('Executing on queue deleted command (ID %s)', queue_id)
        self._on_queue_deleted_manager.on_queue_deleted(queue_id)

    @debug.trace_duration
    def handle_on_agent_paused(self, msg):
        logger.info('Executing on agent paused command (MemberName %s)', msg['MemberName'])
        pause_info = self._get_pause_info(msg)
        self._on_queue_agent_paused_manager.on_queue_agent_paused(*pause_info)

    @debug.trace_duration
    def handle_on_agent_unpaused(self, msg):
        logger.info('Executing on agent unpaused command (MemberName %s)', msg['MemberName'])
        pause_info = self._get_pause_info(msg)
        self._on_queue_agent_paused_manager.on_queue_agent_unpaused(*pause_info)

    @debug.trace_duration
    def handle_on_agent_status_on_call(self, msg):
        call_status = self._get_on_call_status(msg)
        logger.info('Agent has a change on his status call (MemberName %s), is on call : %s', msg['MemberName'], call_status[3])
        self._on_queue_agent_call_manager.on_queue_call_status_changed(*call_status)

    def _get_pause_info(self, msg):
        _, agent_number = msg['MemberName'].split('/', 1)
        reason = msg['PausedReason']
        queue = msg['Queue']
        with db_utils.session_scope():
            agent = self._agent_dao.agent_with_number(agent_number)
        return agent.id, agent_number, reason, queue

    def _get_is_on_call(self, msg):
        if 'AgentConnect' in msg['Event']:
            return True
        if 'AgentComplete' in msg['Event']:
            return False

    def _get_on_call_status(self, msg):
        _, agent_number = msg['MemberName'].split('/', 1)
        queue = msg['Queue']
        on_call = self._get_is_on_call(msg)
        with db_utils.session_scope():
            agent = self._agent_dao.agent_with_number(agent_number)
        return agent.id, agent_number, queue, on_call
