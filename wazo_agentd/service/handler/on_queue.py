# Copyright 2013-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import re

from wazo_agentd.service.helper import is_valid_agent_number

from xivo import debug
from xivo_dao.helpers import db_utils

logger = logging.getLogger(__name__)

AGENT_ID_FROM_IFACE = re.compile(r'^Local/id-(\d+)@agentcallback$')


class OnQueueHandler:
    def __init__(
        self,
        on_queue_added_manager,
        on_queue_updated_manager,
        on_queue_deleted_manager,
        on_queue_agent_paused_manager,
        queue_dao,
        agent_dao,
    ):
        self._on_queue_added_manager = on_queue_added_manager
        self._on_queue_updated_manager = on_queue_updated_manager
        self._on_queue_deleted_manager = on_queue_deleted_manager
        self._on_queue_agent_paused_manager = on_queue_agent_paused_manager
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
        logger.info(
            'Executing on agent paused command (MemberName %s)', msg['MemberName']
        )
        pause_info = self._get_pause_info(msg)
        if not pause_info:
            logger.debug(
                '"%s" is not a valid agent number. Ignoring.',
                self._extract_agent_number(msg['MemberName']),
            )
            return
        self._on_queue_agent_paused_manager.on_queue_agent_paused(*pause_info)

    @debug.trace_duration
    def handle_on_agent_unpaused(self, msg):
        logger.info(
            'Executing on agent unpaused command (MemberName %s)', msg['MemberName']
        )
        pause_info = self._get_pause_info(msg)
        if not pause_info:
            logger.debug(
                '"%s" is not a valid agent number. Ignoring.',
                self._extract_agent_number(msg['MemberName']),
            )
            return
        self._on_queue_agent_paused_manager.on_queue_agent_unpaused(*pause_info)

    def _extract_agent_number(self, member_name):
        _, agent_number = member_name.split('/', 1)
        return agent_number

    def _get_pause_info(self, msg):
        agent_number = self._extract_agent_number(msg['MemberName'])
        if not is_valid_agent_number(agent_number):
            return
        reason = msg['PausedReason']
        queue = msg['Queue']
        if matches := AGENT_ID_FROM_IFACE.match(msg['Interface']):
            agent_id = int(matches.group(1))
            return agent_id, agent_number, reason, queue
