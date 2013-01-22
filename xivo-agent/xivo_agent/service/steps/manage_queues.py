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

import logging

logger = logging.getLogger(__name__)


class AddAgentToQueueStep(object):

    def __init__(self, ami_client):
        self._ami_client = ami_client

    def execute(self, command, response, blackboard):
        agent_status = blackboard.agent_status
        queue = blackboard.queue

        if agent_status is not None:
            self.add_agent_to_queue(agent_status, queue.name)

    def add_agent_to_queue(self, agent_status, queue_name):
        member_name = 'Agent/{0}'.format(agent_status.agent_number)
        skills = 'agent-{0}'.format(agent_status.agent_id)
        action = self._ami_client.queue_add(queue_name, agent_status.interface, member_name, agent_status.state_interface,
                                            skills=skills)
        if not action.success:
            logger.warning('Failure to add interface %r to queue %r', agent_status.interface, queue_name)


class AddAgentToQueuesStep(object):

    def __init__(self, ami_client):
        self._ami_client = ami_client

    def execute(self, command, response, blackboard):
        agent = blackboard.agent
        interface = blackboard.interface
        state_interface = blackboard.state_interface

        member_name = 'Agent/{0}'.format(agent.number)
        for queue in agent.queues:
            action = self._ami_client.queue_add(queue.name, interface, member_name, state_interface,
                                                queue.penalty, queue.skills)
            if not action.success:
                logger.warning('Failure to add interface %r to queue %r', blackboard.interface, queue.name)


class RemoveAgentFromQueueStep(object):

    def __init__(self, ami_client):
        self._ami_client = ami_client

    def execute(self, command, response, blackboard):
        agent_status = blackboard.agent_status
        queue = blackboard.queue

        if agent_status is not None:
            self.remove_agent_from_queue(agent_status, queue.name)

    def remove_agent_from_queue(self, agent_status, queue_name):
        self._ami_client.queue_remove(queue_name, agent_status.interface)


class RemoveAgentFromQueuesStep(object):

    def __init__(self, ami_client):
        self._ami_client = ami_client

    def remove_agent_from_queues(self, agent_status):
        for queue in agent_status.queues:
            self._ami_client.queue_remove(queue.name, agent_status.interface)

    def execute(self, command, response, blackboard):
        agent_status = blackboard.agent_status
        self.remove_agent_from_queues(agent_status)
