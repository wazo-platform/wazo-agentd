# -*- coding: UTF-8 -*-

import unittest
from mock import Mock
from xivo_agent.service.steps import AddAgentToQueueStep
from xivo_agent.service.steps.manage_queues import RemoveAgentFromQueueStep, \
    AddAgentToQueuesStep, RemoveAgentFromQueuesStep


class TestAddAgentToQueueStep(unittest.TestCase):

    def setUp(self):
        self.command = Mock()
        self.response = Mock()
        self.response.error = None
        self.blackboard = Mock()
        self.agent = Mock()
        self.agent.id = 42
        self.agent.number = '456'
        self.queue = Mock()
        self.queue.name = 'foobar1'
        self.blackboard.agent = self.agent
        self.blackboard.queue = self.queue

    def test_execute_when_logged(self):
        self.blackboard.agent_status.interface = 'Local/2@foobar'
        self.blackboard.agent_status.state_interface = 'SIP/abcdef'
        ami_client = Mock()

        step = AddAgentToQueueStep(ami_client)
        step.execute(self.command, self.response, self.blackboard)

        ami_client.queue_add.assert_called_once_with(self.queue.name,
                                                     self.blackboard.agent_status.interface,
                                                     'Agent/%s' % self.blackboard.agent.number,
                                                     self.blackboard.agent_status.state_interface,
                                                     skills='agent-{0}'.format(self.agent.id))

    def test_execute_when_not_logged(self):
        self.blackboard.agent_status = None
        agent_client = Mock()

        step = AddAgentToQueueStep(agent_client)
        step.execute(self.command, self.response, self.blackboard)

        self.assertFalse(agent_client.queue_add.called)


class TestAddAgentToQueuesStep(unittest.TestCase):

    def setUp(self):
        self.ami_client = Mock()
        self.step = AddAgentToQueuesStep(self.ami_client)
        self.command = Mock()
        self.response = Mock()
        self.response.error = None
        self.blackboard = Mock()
        self.agent = Mock()
        self.queue = Mock()
        self.agent.queues = [self.queue]
        self.blackboard.agent = self.agent
        self.blackboard.interface = 'Local/2@foobar'
        self.blackboard.state_interface = 'SIP/abcdef'

    def test_execute(self):
        self.agent.number = '456'
        self.queue.name = 'foobar'
        self.queue.penalty = 1
        self.queue.skills = 'agent-32'

        self.step.execute(self.command, self.response, self.blackboard)

        self.ami_client.queue_add.assert_called_once_with(self.queue.name,
                                                          self.blackboard.interface,
                                                         'Agent/%s' % self.agent.number,
                                                         self.blackboard.state_interface,
                                                         self.queue.penalty,
                                                         self.queue.skills)


class TestRemoveAgentFromQueueStep(unittest.TestCase):

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

        step = RemoveAgentFromQueueStep(agent_client)
        step.execute(self.command, self.response, self.blackboard)

        agent_client.queue_remove.assert_called_once_with(self.blackboard.queue.name,
                                                          self.blackboard.agent_status.interface)

    def test_execute_when_not_logged(self):
        self.blackboard.agent_status = None
        agent_client = Mock()

        step = RemoveAgentFromQueueStep(agent_client)
        step.execute(self.command, self.response, self.blackboard)

        self.assertFalse(agent_client.queue_remove.called)


class TestRemoveAgentFromQueuesStep(unittest.TestCase):

    def setUp(self):
        self.ami_client = Mock()
        self.step = RemoveAgentFromQueuesStep(self.ami_client)
        self.command = Mock()
        self.response = Mock()
        self.response.error = None
        self.blackboard = Mock()
        self.queue = Mock()
        self.queue.name = 'queue1'
        self.agent_status = Mock()
        self.agent_status.interface = 'Local/1@foo'
        self.agent_status.queues = [self.queue]
        self.blackboard.agent_status = self.agent_status

    def test_execute(self):
        self.step.execute(self.command, self.response, self.blackboard)

        self.ami_client.queue_remove.assert_called_once_with(self.queue.name,
                                                             self.agent_status.interface)
