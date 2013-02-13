# -*- coding: utf-8 -*-

# Copyright (C) 2013  Avencall
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

from xivo_agent.exception import AgentNotLoggedError


class PauseManager(object):

    def __init__(self, pause_action):
        self._pause_action = pause_action

    def pause_agent(self, agent_status):
        self._check_agent_status(agent_status)
        self._pause_action.pause_agent(agent_status)

    def unpause_agent(self, agent_status):
        self._check_agent_status(agent_status)
        self._pause_action.unpause_agent(agent_status)

    def _check_agent_status(self, agent_status):
        if agent_status is None:
            raise AgentNotLoggedError()
