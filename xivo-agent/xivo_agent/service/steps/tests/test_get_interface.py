# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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
