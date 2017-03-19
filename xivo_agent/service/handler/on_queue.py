# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import logging

from xivo import debug
from xivo_dao.helpers import db_utils

logger = logging.getLogger(__name__)


class OnQueueHandler(object):

    def __init__(self, on_queue_added_manager, on_queue_updated_manager, on_queue_deleted_manager, on_queue_agent_paused_manager, queue_dao):
        self._on_queue_added_manager = on_queue_added_manager
        self._on_queue_updated_manager = on_queue_updated_manager
        self._on_queue_deleted_manager = on_queue_deleted_manager
        self._on_queue_agent_paused_manager = on_queue_agent_paused_manager
        self._queue_dao = queue_dao

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
        self._on_queue_agent_paused_manager.on_queue_agent_paused(msg)

    @debug.trace_duration
    def handle_on_agent_unpaused(self, msg):
        logger.info('Executing on agent unpaused command (MemberName %s)', msg['MemberName'])
        self._on_queue_agent_paused_manager.on_queue_agent_unpaused(msg)
