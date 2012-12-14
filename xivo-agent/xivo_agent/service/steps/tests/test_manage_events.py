# -*- coding: UTF-8 -*-

import unittest
from mock import Mock
from xivo_agent.service.steps import SendAgentAddedToQueueEventStep


class TestSendAgentAddedToQueueEventStep(unittest.TestCase):

    def setUp(self):
        self.command = Mock()
        self.response = Mock()
        self.response.error = None
        self.blackboard = Mock()
        self.blackboard.agent.id = 123
        self.blackboard.agent.number = '456'
        self.blackboard.queue.name = 'queue1'

    def test_execute(self):
        agent_client = Mock()

        step = SendAgentAddedToQueueEventStep(agent_client)
        step.execute(self.command, self.response, self.blackboard)

        agent_client.agent_added_to_queue.assert_called_once_with(self.blackboard.agent.id,
                                                                  self.blackboard.agent.number,
                                                                  self.blackboard.queue.name)
