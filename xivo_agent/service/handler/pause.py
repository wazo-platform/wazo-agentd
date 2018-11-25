# Copyright (C) 2013-2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

import logging

from xivo import debug
from xivo_dao.helpers import db_utils

logger = logging.getLogger(__name__)


class PauseHandler(object):

    def __init__(self, pause_manager, agent_status_dao):
        self._pause_manager = pause_manager
        self._agent_status_dao = agent_status_dao

    @debug.trace_duration
    def handle_pause_by_number(self, agent_number, reason):
        logger.info('Executing pause command (number %s)', agent_number)
        with db_utils.session_scope():
            agent_status = self._agent_status_dao.get_status_by_number(agent_number)
        self._pause_manager.pause_agent(agent_status, reason)

    @debug.trace_duration
    def handle_unpause_by_number(self, agent_number):
        logger.info('Executing unpause command (number %s)', agent_number)
        with db_utils.session_scope():
            agent_status = self._agent_status_dao.get_status_by_number(agent_number)
        self._pause_manager.unpause_agent(agent_status)
