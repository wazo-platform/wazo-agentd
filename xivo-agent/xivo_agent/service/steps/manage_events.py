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

class SendAgentAddedToQueueEventStep(object):

    def __init__(self, ami_client):
        self._ami_client = ami_client

    def execute(self, command, response, blackboard):
        agent_id = blackboard.agent.id
        agent_number = blackboard.agent.number
        queue_name = blackboard.queue.name

        self._ami_client.agent_added_to_queue(agent_id, agent_number, queue_name)


class SendAgentRemovedFromQueueEventStep(object):

    def __init__(self, ami_client):
        self._ami_client = ami_client

    def execute(self, command, response, blackboard):
        agent_id = blackboard.agent.id
        agent_number = blackboard.agent.number
        queue_name = blackboard.queue.name

        self._ami_client.agent_removed_from_queue(agent_id, agent_number, queue_name)


class SendAgentLoginEventStep(object):

    def __init__(self, ami_client):
        self._ami_client = ami_client

    def execute(self, command, response, blackboard):
        self._ami_client.agent_login(blackboard.agent.id, blackboard.agent.number, blackboard.extension, blackboard.context)


class SendAgentLogoffEventStep(object):

    def __init__(self, ami_client):
        self._ami_client = ami_client

    def execute(self, command, response, blackboard):
        agent_status = blackboard.agent_status

        self.send_agent_logoff(agent_status.agent_id, agent_status.agent_number)

    def send_agent_logoff(self, agent_id, agent_number):
        self._ami_client.agent_logoff(agent_id, agent_number)
