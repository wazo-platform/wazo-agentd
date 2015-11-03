# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import logging

from xivo import debug
from xivo_dao.helpers import db_utils

logger = logging.getLogger(__name__)


class PauseHandler(object):

    def __init__(self, pause_manager, agent_status_dao):
        self._pause_manager = pause_manager
        self._agent_status_dao = agent_status_dao

    @debug.trace_duration
    def handle_pause_by_number(self, agent_number):
        logger.info('Executing pause command (number %s)', agent_number)
        with db_utils.session_scope():
            agent_status = self._agent_status_dao.get_status_by_number(agent_number)
        self._pause_manager.pause_agent(agent_status)

    @debug.trace_duration
    def handle_unpause_by_number(self, agent_number):
        logger.info('Executing unpause command (number %s)', agent_number)
        with db_utils.session_scope():
            agent_status = self._agent_status_dao.get_status_by_number(agent_number)
        self._pause_manager.unpause_agent(agent_status)
