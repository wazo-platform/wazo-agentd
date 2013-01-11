# -*- coding: UTF-8 -*-

import unittest
from mock import Mock
from xivo_agent.service.steps import SendAgentAddedToQueueEventStep
from xivo_agent.service.steps.manage_events import SendAgentRemovedFromQueueEventStep,\
    SendAgentLogoffEventStep


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


class TestSendAgentRemovedFromQueueEventStep(unittest.TestCase):

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

        step = SendAgentRemovedFromQueueEventStep(agent_client)
        step.execute(self.command, self.response, self.blackboard)

        agent_client.agent_removed_from_queue.assert_called_once_with(self.blackboard.agent.id,
                                                                      self.blackboard.agent.number,
                                                                      self.blackboard.queue.name)


class TestSendLogoffEventStep(unittest.TestCase):

    def setUp(self):
        self.command = Mock()
        self.response = Mock()
        self.response.error = None
        self.blackboard = Mock()
        self.blackboard.agent_status.agent_id = 123
        self.blackboard.agent_status.agent_number = '456'

    def test_execute(self):
        agent_client = Mock()

        step = SendAgentLogoffEventStep(agent_client)
        step.execute(self.command, self.response, self.blackboard)

        agent_client.agent_logoff.assert_called_once_with(self.blackboard.agent_status.agent_id,
                                                          self.blackboard.agent_status.agent_number)
