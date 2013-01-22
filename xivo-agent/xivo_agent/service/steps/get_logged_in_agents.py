# -*- coding: utf-8 -*-

# Copyright (C) 2012-2013 Avencall
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

class GetLoggedInAgentsStep(object):

    def __init__(self, agent_status_dao, agent_dao):
        self._agent_status_dao = agent_status_dao
        self._agent_dao = agent_dao

    def execute(self, command, response, blackboard):
        agent_ids = self._logged_in_agent_ids()
        blackboard.logged_in_agents = map(self._get_agent_and_status, agent_ids)

    def _logged_in_agent_ids(self):
        return (status.agent_id for status in self._agent_status_dao.get_statuses() if status.logged)

    def _get_agent_and_status(self, agent_id):
        return (
            self._agent_dao.agent_with_id(agent_id),
            self._agent_status_dao.get_status(agent_id)
        )
