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

    def test_add_logoff_cmd(self):
        command = commands.LogoffCommand
        callback = self.agent_service._exec_logoff_cmd

        self.agent_service._add_logoff_cmd(self.step_factory)

        self.assertTrue(command.name in self.agent_service._steps)
        self.agent_server.add_command.assert_called_once_with(command, callback)

    def test_add_add_to_queue_cmd(self):
        self.agent_service._add_cmd = Mock()
        expected = [
            call.get_agent(),
            call.get_agent_status(),
            call.get_queue(),
            call.check_agent_is_not_member_of_queue(),
            call.insert_agent_into_queuemember(),
            call.send_agent_added_to_queue_event(),
            call.add_agent_to_queue(),
            call.update_agent_status(),
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
            call.send_agent_removed_from_queue_event(),
            call.remove_agent_from_queue(),
            call.update_agent_status(),
        ]

        self.agent_service._add_remove_from_queue_cmd(self.step_factory)

        self.assertEqual(self.step_factory.mock_calls, expected)

    def test_add_on_agent_updated_cmd(self):
        self.agent_service._add_on_agent_updated_cmd(self.step_factory)

        self.agent_server.add_command.assert_called_once_with(
            commands.OnAgentUpdatedCommand,
            self.agent_service._exec_on_agent_updated_cmd)

    def test_add_on_agent_deleted_cmd(self):
        self.agent_service._add_on_agent_deleted_cmd(self.step_factory)

        self.agent_server.add_command.assert_called_once_with(
            commands.OnAgentDeletedCommand,
            self.agent_service._exec_on_agent_deleted_cmd)

    def test_add_on_queue_added_cmd(self):
        self.agent_service._add_on_queue_added_cmd(self.step_factory)

        self.agent_server.add_command.assert_called_once_with(
            commands.OnQueueAddedCommand,
            self.agent_service._exec_on_queue_added_cmd)

    def test_add_on_queue_updated_cmd(self):
        self.agent_service._add_on_queue_updated_cmd(self.step_factory)

        self.agent_server.add_command.assert_called_once_with(
            commands.OnQueueUpdatedCommand,
            self.agent_service._exec_on_queue_updated_cmd)

    def test_add_on_queue_deleted_cmd(self):
        self.agent_service._add_on_queue_deleted_cmd(self.step_factory)

        self.agent_server.add_command.assert_called_once_with(
            commands.OnQueueDeletedCommand,
            self.agent_service._exec_on_queue_deleted_cmd)

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

    def test_exec_on_agent_updated_cmd(self):
        agent_id = 42
        command = commands.OnAgentUpdatedCommand(agent_id)
        response = CommandResponse()
        on_agent_updated_manager = Mock()
        self.agent_service._on_agent_updated_manager = on_agent_updated_manager

        self.agent_service._exec_on_agent_updated_cmd(command, response)

        on_agent_updated_manager.on_agent_updated.assert_called_once_with(agent_id)

    def test_exec_on_agent_deleted_cmd(self):
        agent_id = 42
        command = commands.OnAgentDeletedCommand(agent_id)
        response = CommandResponse()
        on_agent_deleted_manager = Mock()
        self.agent_service._on_agent_deleted_manager = on_agent_deleted_manager

        self.agent_service._exec_on_agent_deleted_cmd(command, response)

        on_agent_deleted_manager.on_agent_deleted.assert_called_once_with(agent_id)
