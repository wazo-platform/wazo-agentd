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

class InsertAgentIntoQueuememberStep(object):

    def __init__(self, queue_member_dao):
        self._queue_member_dao = queue_member_dao

    def execute(self, command, response, blackboard):
        agent_id = blackboard.agent.id
        agent_number = blackboard.agent.number
        queue_name = blackboard.queue.name

        self._queue_member_dao.add_agent_to_queue(agent_id, agent_number, queue_name)


class DeleteAgentFromQueuememberStep(object):

    def __init__(self, queue_member_dao):
        self._queue_member_dao = queue_member_dao

    def execute(self, command, response, blackboard):
        agent_id = blackboard.agent.id
        queue_name = blackboard.queue.name

        self._queue_member_dao.remove_agent_from_queue(agent_id, queue_name)
