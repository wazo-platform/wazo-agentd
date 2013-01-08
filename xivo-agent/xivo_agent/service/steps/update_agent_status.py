# -*- coding: UTF-8 -*-

# Copyright (C) 2012-2013  Avencall
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

from xivo_agent.ctl import commands


class UpdateAgentStatusStep(object):

    def __init__(self, agent_login_dao):
        self._agent_login_dao = agent_login_dao

    def execute(self, command, response, blackboard):
        if command.name == commands.LoginCommand.name:
            self.log_in_agent(blackboard.agent, blackboard.extension, blackboard.context, blackboard.interface)
        elif command.name == commands.LogoffCommand.name:
            self.log_off_agent(blackboard.agent)

    def log_in_agent(self, agent, extension, context, interface):
        self._agent_login_dao.log_in_agent(agent.id, extension, context, interface)

    def log_off_agent(self, agent):
        self._agent_login_dao.log_off_agent(agent.id)
