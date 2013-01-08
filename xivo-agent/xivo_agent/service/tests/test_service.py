# -*- coding: UTF-8 -*-

# Copyright (C) 2012-2013  Avencall
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
from mock import Mock, call, patch
from xivo_agent.ctl import commands
from xivo_agent.ctl.response import CommandResponse
from xivo_agent.ctl.server import AgentServer
from xivo_agent.service.factory import StepFactory
from xivo_agent.service.service import AgentService
from xivo_agent.service.steps import GetAgentStatusesStep


class TestAgentService(unittest.TestCase):

    def setUp(self):
        self.agent_server = Mock(AgentServer)
        self.agent_service = AgentService(self.agent_server)
        self.step_factory = Mock(StepFactory)

    def test_add_add_to_queue_cmd(self):
        self.agent_service._add_cmd = Mock()
        expected = [
            call.get_agent(),
            call.get_agent_status(),
            call.get_queue(),
            call.check_agent_is_not_member_of_queue(),
            call.insert_agent_into_queuemember(),
            call.add_agent_to_queue(),
            call.send_agent_added_to_queue_event(),
        ]

        self.agent_service._add_add_to_queue_cmd(self.step_factory)

        self.assertEqual(self.step_factory.mock_calls, expected)

    def test_add_remove_from_queue_cmd(self):
        self.agent_service._add_cmd = Mock()
        expected = [
            call.get_agent(),
            call.get_agent_status(),
            call.get_queue(),
            call.check_agent_is_member_of_queue(),
            call.delete_agent_from_queuemember(),
            call.remove_agent_from_queue(),
            call.send_agent_removed_from_queue_event(),
        ]

        self.agent_service._add_remove_from_queue_cmd(self.step_factory)

        self.assertEqual(self.step_factory.mock_calls, expected)

    @patch('xivo_agent.service.service.Blackboard')
    def test_exec_status_cmd_when_logged_in(self, mock_blackboard):
        mock_blackboard_instance = Mock()
        mock_blackboard.return_value = mock_blackboard_instance
        mock_blackboard_instance.agent.id = 42
        mock_blackboard_instance.agent.number = '1'
        mock_blackboard_instance.agent_status.extension = '1001'
        mock_blackboard_instance.agent_status.context = 'default'
        command = commands.StatusCommand()
        response = CommandResponse()
        self.agent_service._steps[command.name] = []

        self.agent_service._exec_status_cmd(command, response)

        self.assertEqual(response.value['id'], mock_blackboard_instance.agent.id)
        self.assertEqual(response.value['number'], mock_blackboard_instance.agent.number)
        self.assertEqual(response.value['logged'], True)
        self.assertEqual(response.value['extension'], mock_blackboard_instance.agent_status.extension)
        self.assertEqual(response.value['context'], mock_blackboard_instance.agent_status.context)

    @patch('xivo_agent.service.service.Blackboard')
    def test_exec_status_cmd_when_not_logged_in(self, mock_blackboard):
        mock_blackboard_instance = Mock()
        mock_blackboard.return_value = mock_blackboard_instance
        mock_blackboard_instance.agent.id = 42
        mock_blackboard_instance.agent.number = '1'
        mock_blackboard_instance.agent_status = None
        command = commands.StatusCommand()
        response = CommandResponse()
        self.agent_service._steps[command.name] = []

        self.agent_service._exec_status_cmd(command, response)

        self.assertEqual(response.value['id'], mock_blackboard_instance.agent.id)
        self.assertEqual(response.value['number'], mock_blackboard_instance.agent.number)
        self.assertEqual(response.value['logged'], False)
        self.assertEqual(response.value['extension'], None)
        self.assertEqual(response.value['context'], None)

    @patch('xivo_agent.service.service.Blackboard')
    def test_exec_statuses_cmd(self, mock_blackboard):
        mock_blackboard_instance = Mock()
        mock_blackboard.return_value = mock_blackboard_instance
        mock_blackboard_instance.agent_statuses = []
        statuses_command = commands.StatusesCommand()
        response = CommandResponse()

        mock_step = Mock(GetAgentStatusesStep)
        self.agent_service._steps['statuses'] = [mock_step]

        self.agent_service._exec_statuses_cmd(statuses_command, response)

        mock_step.execute.assert_called_once_with(statuses_command,
                                                  response,
                                                  mock_blackboard_instance)
