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

    def __init__(self, agent_status_dao):
        self._agent_status_dao = agent_status_dao

    def execute(self, command, response, blackboard):
        if command.name == commands.LoginCommand.name:
            self.log_in_agent(blackboard.agent, blackboard.extension, blackboard.context, blackboard.interface, blackboard.state_interface)
        elif command.name == commands.LogoffCommand.name:
            self.log_off_agent(blackboard.agent.id)
        elif command.name == commands.AddToQueueCommand.name:
            if blackboard.agent_status is not None:
                self.add_agent_to_queue(blackboard.agent.id, blackboard.queue)
        elif command.name == commands.RemoveFromQueueCommand.name:
            if blackboard.agent_status is not None:
                self.remove_agent_from_queue(blackboard.agent.id, blackboard.queue.id)

    def log_in_agent(self, agent, extension, context, interface, state_interface):
        self._agent_status_dao.log_in_agent(agent.id, agent.number, extension, context, interface, state_interface)
        self._agent_status_dao.add_agent_to_queues(agent.id, agent.queues)

    def log_off_agent(self, agent_id):
        self._agent_status_dao.log_off_agent(agent_id)
        self._agent_status_dao.remove_agent_from_all_queues(agent_id)

    def add_agent_to_queue(self, agent_id, queue):
        self._agent_status_dao.add_agent_to_queues(agent_id, [queue])

    def remove_agent_from_queue(self, agent_id, queue_id):
        self._agent_status_dao.remove_agent_from_queues(agent_id, [queue_id])

    def remove_all_agents_from_queue(self, queue_id):
        self._agent_status_dao.remove_all_agents_from_queue(queue_id)
