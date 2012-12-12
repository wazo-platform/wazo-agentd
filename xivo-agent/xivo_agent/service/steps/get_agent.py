# -*- coding: UTF-8 -*-

# Copyright (C) 2012  Avencall
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

from xivo_agent.ctl import error


class GetAgentStep(object):

    def __init__(self, agent_dao):
        self._agent_dao = agent_dao

    def execute(self, command, response, blackboard):
        try:
            if command.agent_id is not None:
                blackboard.agent = self._agent_dao.agent_with_id(command.agent_id)
            else:
                blackboard.agent = self._agent_dao.agent_with_number(command.agent_number)
        except LookupError:
            response.error = error.NO_SUCH_AGENT
