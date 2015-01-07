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

from xivo_agent.exception import AgentNotLoggedError
from xivo_agent.service.manager.login import LogManagerMixin


class LogoffManager(LogManagerMixin):

    agent_status = 'logged_out'

    def __init__(self, logoff_action, agent_status_dao, bus_producer, config):
        super(LogoffManager, self).__init__(bus_producer, config)
        self._logoff_action = logoff_action
        self._agent_status_dao = agent_status_dao

    def logoff_agent(self, agent_status):
        if agent_status is None:
            raise AgentNotLoggedError()
        self._logoff_action.logoff_agent(agent_status)
        self._send_bus_status_update(agent_status.agent_id)

    def logoff_all_agents(self):
        agent_statuses = self._get_agent_statuses()
        for agent_status in agent_statuses:
            self._logoff_action.logoff_agent(agent_status)

    def _get_agent_statuses(self):
        agent_ids = self._agent_status_dao.get_logged_agent_ids()
        return [self._agent_status_dao.get_status(agent_id) for agent_id in agent_ids]
