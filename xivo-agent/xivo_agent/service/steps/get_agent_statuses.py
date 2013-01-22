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

class GetAgentStatusesStep(object):

    def __init__(self, agent_status_dao):
        self._agent_status_dao = agent_status_dao

    def execute(self, command, response, blackboard):
        blackboard.agent_statuses = self.get_statuses()

    def get_statuses(self):
        return self._agent_status_dao.get_statuses()

    def get_statuses_of_logged_agent_for_queue(self, queue_id):
        return self._agent_status_dao.get_statuses_of_logged_agent_for_queue(queue_id)
