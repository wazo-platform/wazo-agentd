# -*- coding: UTF-8 -*-

import unittest
from mock import Mock
from xivo_agent.ctl import error
from xivo_agent.service.steps import CheckAgentIsLoggedStep, CheckAgentIsNotLoggedStep


class TestCheckAgentIsLoggedStep(unittest.TestCase):

    def test_execute_when_logged(self):
        command = Mock()
        response = Mock()
        response.error = None
        blackboard = Mock()
        blackboard.agent_status = Mock()

        step = CheckAgentIsLoggedStep()
        step.execute(command, response, blackboard)

        self.assertEqual(response.error, None)

    def test_execute_when_not_logged(self):
        command = Mock()
        response = Mock()
        response.error = None
        blackboard = Mock()
        blackboard.agent_status = None

        step = CheckAgentIsLoggedStep()
        step.execute(command, response, blackboard)

        self.assertEqual(response.error, error.NOT_LOGGED)


class TestCheckAgentIsNotLoggedStep(unittest.TestCase):

    def test_execute_when_not_logged(self):
        command = Mock()
        response = Mock()
        response.error = None
        blackboard = Mock()
        blackboard.agent_status = None

        step = CheckAgentIsNotLoggedStep()
        step.execute(command, response, blackboard)

        self.assertEqual(response.error, None)

    def test_execute_when_logged(self):
        command = Mock()
        response = Mock()
        response.error = None
        blackboard = Mock()
        blackboard.agent_status = Mock()

        step = CheckAgentIsNotLoggedStep()
        step.execute(command, response, blackboard)

        self.assertEqual(response.error, error.ALREADY_LOGGED)
