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
