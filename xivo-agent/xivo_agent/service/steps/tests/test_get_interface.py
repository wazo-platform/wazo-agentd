# -*- coding: UTF-8 -*-

import unittest
from mock import Mock
from xivo_agent.ctl import error
from xivo_agent.service.steps import GetStateInterfaceForExtensionStep
from xivo_agent.service.steps.get_interface import GetInterfaceStep


class TestGetInterfaceStep(unittest.TestCase):

    def test_execute(self):
        command = Mock()
        response = Mock()
        blackboard = Mock()
        blackboard.agent.id = 42
        step = GetInterfaceStep()

        step.execute(command, response, blackboard)

        self.assertEqual(blackboard.interface, 'Local/id-42@agentcallback')


class TestGetInterfaceForExtensionStep(unittest.TestCase):

    def test_execute_with_known_exten(self):
        command = Mock()
        response = Mock()
        blackboard = Mock()
        blackboard.extension = '1001'
        blackboard.context = 'default'

        interface = Mock()
        line_dao = Mock()
        line_dao.get_interface_from_exten_and_context.return_value = interface

        step = GetStateInterfaceForExtensionStep(line_dao)
        step.execute(command, response, blackboard)

        line_dao.get_interface_from_exten_and_context.assert_called_once_with(blackboard.extension, blackboard.context)
        self.assertEqual(blackboard.state_interface, interface)

    def test_execute_with_unknown_exten(self):
        command = Mock()
        response = Mock()
        blackboard = Mock()
        blackboard.extension = '1001'
        blackboard.context = 'default'

        line_dao = Mock()
        line_dao.get_interface_from_exten_and_context.side_effect = LookupError()

        step = GetStateInterfaceForExtensionStep(line_dao)
        step.execute(command, response, blackboard)

        line_dao.get_interface_from_exten_and_context.assert_called_once_with(blackboard.extension, blackboard.context)
        self.assertEqual(response.error, error.NO_SUCH_EXTEN)
