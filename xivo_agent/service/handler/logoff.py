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

logger = logging.getLogger(__name__)


class LogoffHandler(object):

    def __init__(self, logoff_manager, agent_status_dao):
        self._logoff_manager = logoff_manager
        self._agent_status_dao = agent_status_dao

    @debug.trace_duration
    def handle_logoff_by_id(self, agent_id):
        logger.info('Executing logoff command (ID %s)', agent_id)
        agent_status = self._agent_status_dao.get_status(agent_id)
        self._handle_logoff(agent_status)

    @debug.trace_duration
    def handle_logoff_by_number(self, agent_number):
        logger.info('Executing logoff command (number %s)', agent_number)
        agent_status = self._agent_status_dao.get_status_by_number(agent_number)
        self._handle_logoff(agent_status)

    @debug.trace_duration
    def handle_logoff_all(self):
        logger.info('Executing logoff all command')
        self._logoff_manager.logoff_all_agents()

    def _handle_logoff(self, agent_status):
        self._logoff_manager.logoff_agent(agent_status)
