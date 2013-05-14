# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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
from xivo_agent import command as commands

logger = logging.getLogger(__name__)


class LogoffHandler(object):

    def __init__(self, logoff_manager, agent_status_dao):
        self._logoff_manager = logoff_manager
        self._agent_status_dao = agent_status_dao

    def register_commands(self, agent_server):
        agent_server.add_command(commands.LogoffByIDCommand, self.handle_logoff_by_id)
        agent_server.add_command(commands.LogoffByNumberCommand, self.handle_logoff_by_number)
        agent_server.add_command(commands.LogoffAllCommand, self.handle_logoff_all)

    @debug.trace_duration
    def handle_logoff_by_id(self, command):
        logger.info('Executing logoff command (ID %s)', command.agent_id)
        agent_status = self._agent_status_dao.get_status(command.agent_id)
        self._handle_logoff(agent_status)

    @debug.trace_duration
    def handle_logoff_by_number(self, command):
        logger.info('Executing logoff command (number %s)', command.agent_number)
        agent_status = self._agent_status_dao.get_status_by_number(command.agent_number)
        self._handle_logoff(agent_status)

    @debug.trace_duration
    def handle_logoff_all(self, command):
        logger.info('Executing logoff all command')
        self._logoff_manager.logoff_all_agents()

    def _handle_logoff(self, agent_status):
        self._logoff_manager.logoff_agent(agent_status)
