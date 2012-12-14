# -*- coding: UTF-8 -*-

import unittest
from mock import Mock
from xivo_agent.ctl import error
from xivo_agent.service.steps import CheckAgentIsNotMemberOfQueueStep
from xivo_agent.service.steps.check_agent_membership import CheckAgentIsMemberOfQueueStep


class TestCheckAgentIsMemberOfQueueStep(unittest.TestCase):

    def setUp(self):
        self.command = Mock()
        self.response = Mock()
        self.response.error = None
        self.blackboard = Mock()
        self.blackboard.queue.name = 'foobar1'

    def test_execute_when_is_member(self):
        agent_queue = Mock()
        agent_queue.name = 'foobar1'
        self.blackboard.agent.queues = [agent_queue]

        step = CheckAgentIsMemberOfQueueStep()
        step.execute(self.command, self.response, self.blackboard)

        self.assertEqual(self.response.error, None)

    def test_execute_when_is_not_member(self):
        self.blackboard.agent.queues = []

        step = CheckAgentIsMemberOfQueueStep()
        step.execute(self.command, self.response, self.blackboard)

        self.assertEqual(self.response.error, error.NOT_IN_QUEUE)


class TestCheckAgentIsNotMemberOfQueueStep(unittest.TestCase):

    def setUp(self):
        self.command = Mock()
        self.response = Mock()
        self.response.error = None
        self.blackboard = Mock()
        self.blackboard.queue.name = 'foobar1'

    def test_execute_when_is_not_member(self):
        self.blackboard.agent.queues = []

        step = CheckAgentIsNotMemberOfQueueStep()
        step.execute(self.command, self.response, self.blackboard)

        self.assertEqual(self.response.error, None)

    def test_execute_when_is_member(self):
        agent_queue = Mock()
        agent_queue.name = 'foobar1'
        self.blackboard.agent.queues = [agent_queue]

        step = CheckAgentIsNotMemberOfQueueStep()
        step.execute(self.command, self.response, self.blackboard)

        self.assertEqual(self.response.error, error.ALREADY_IN_QUEUE)
