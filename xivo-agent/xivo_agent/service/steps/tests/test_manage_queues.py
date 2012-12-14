# -*- coding: UTF-8 -*-

import unittest
from mock import Mock
from xivo_agent.service.steps import AddAgentToQueueStep


class TestAddAgentToQueueStep(unittest.TestCase):

    def setUp(self):
        self.command = Mock()
        self.response = Mock()
        self.response.error = None
        self.blackboard = Mock()
        self.blackboard.queue.name = 'foobar1'
        self.blackboard.agent.number = '456'

    def test_execute_when_logged(self):
        self.blackboard.agent_status.interface = 'SIP/abcdef'
        agent_client = Mock()

        step = AddAgentToQueueStep(agent_client)
        step.execute(self.command, self.response, self.blackboard)

        agent_client.queue_add.assert_called_once_with(self.blackboard.queue.name,
                                                       self.blackboard.agent_status.interface,
                                                       'Agent/%s' % self.blackboard.agent.number)

    def test_execute_when_not_logged(self):
        self.blackboard.agent_status = None
        agent_client = Mock()

        step = AddAgentToQueueStep(agent_client)
        step.execute(self.command, self.response, self.blackboard)

        self.assertFalse(agent_client.queue_add.called)
