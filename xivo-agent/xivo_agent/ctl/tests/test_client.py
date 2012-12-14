# -*- coding: UTF-8 -*-

# Copyright (C) 2012  Avencall
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
from mock import Mock, patch
from xivo_agent.ctl.client import AgentClient


class TestAgentClient(unittest.TestCase):

    def setUp(self):
        self.agent_client = AgentClient()

    @patch('xivo_agent.ctl.commands.AddToQueueCommand')
    def test_add_agent_to_queue(self, AddToQueueCommand):
        agent_id = 42
        queue_id = 1
        command = Mock()
        AddToQueueCommand.return_value = command
        self.agent_client._execute_command = Mock()

        self.agent_client.add_agent_to_queue(agent_id, queue_id)

        AddToQueueCommand.assert_called_once_with(agent_id, queue_id)
        self.agent_client._execute_command.assert_called_once_with(command)

    @patch('xivo_agent.ctl.commands.RemoveFromQueueCommand')
    def test_remove_agent_from_queue(self, RemoveFromQueueCommand):
        agent_id = 42
        queue_id = 1
        command = Mock()
        RemoveFromQueueCommand.return_value = command
        self.agent_client._execute_command = Mock()

        self.agent_client.remove_agent_from_queue(agent_id, queue_id)

        RemoveFromQueueCommand.assert_called_once_with(agent_id, queue_id)
        self.agent_client._execute_command.assert_called_once_with(command)
