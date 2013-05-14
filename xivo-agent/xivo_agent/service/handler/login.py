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


class LoginHandler(object):

    def __init__(self, login_manager, agent_dao):
        self._login_manager = login_manager
        self._agent_dao = agent_dao

    def register_commands(self, agent_server):
        agent_server.add_command(commands.LoginByIDCommand, self.handle_login_by_id)
        agent_server.add_command(commands.LoginByNumberCommand, self.handle_login_by_number)

    @debug.trace_duration
    def handle_login_by_id(self, command):
        logger.info('Executing login command (ID %s) on %s@%s', command.agent_id, command.extension, command.context)
        agent = self._agent_dao.get_agent(command.agent_id)
        self._handle_login(agent, command)

    @debug.trace_duration
    def handle_login_by_number(self, command):
        logger.info('Executing login command (number %s) on %s@%s', command.agent_number, command.extension, command.context)
        agent = self._agent_dao.get_agent_by_number(command.agent_number)
        self._handle_login(agent, command)

    def _handle_login(self, agent, command):
        self._login_manager.login_agent(agent, command.extension, command.context)
