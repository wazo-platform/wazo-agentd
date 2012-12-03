# -*- coding: UTF-8 -*-

import logging

logger = logging.getLogger(__name__)


class AddAgentsToQueuesStep(object):

    def __init__(self, ami_client):
        self._ami_client = ami_client

    def execute(self, command, response, blackboard):
        agent = blackboard.agent

        member_name = 'Agent/%s' % agent.number
        for queue in agent.queues:
            action = self._ami_client.queue_add(queue.name, blackboard.interface, member_name)
            if not action.success:
                logger.warning('Failure to add interface %r to queue %r', blackboard.interface, queue.name)


class RemoveAgentsFromQueuesStep(object):

    def __init__(self, ami_client):
        self._ami_client = ami_client

    def execute(self, command, response, blackboard):
        agent = blackboard.agent

        for queue in agent.queues:
            self._ami_client.queue_remove(queue.name, blackboard.agent_status.interface)
