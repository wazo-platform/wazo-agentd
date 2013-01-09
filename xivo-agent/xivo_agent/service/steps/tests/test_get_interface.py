# -*- coding: UTF-8 -*-

import unittest
from mock import Mock
from xivo_agent.ctl import error
from xivo_agent.service.steps import GetInterfaceForExtensionStep


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

        step = GetInterfaceForExtensionStep(line_dao)
        step.execute(command, response, blackboard)

        line_dao.get_interface_from_exten_and_context.assert_called_once_with(blackboard.extension, blackboard.context)
        self.assertEqual(blackboard.interface, interface)

    def test_execute_with_unknown_exten(self):
        command = Mock()
        response = Mock()
        blackboard = Mock()
        blackboard.extension = '1001'
        blackboard.context = 'default'

        line_dao = Mock()
        line_dao.get_interface_from_exten_and_context.side_effect = LookupError()

        step = GetInterfaceForExtensionStep(line_dao)
        step.execute(command, response, blackboard)

        line_dao.get_interface_from_exten_and_context.assert_called_once_with(blackboard.extension, blackboard.context)
        self.assertEqual(response.error, error.NO_SUCH_EXTEN)
