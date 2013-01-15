# -*- coding: UTF-8 -*-

# Copyright (C) 2013  Avencall
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
from xivo_agent.ctl import commands
from xivo_agent.service.steps.update_agent_status import UpdateAgentStatusStep


class TestUpdateAgentStatusStep(unittest.TestCase):

    def setUp(self):
        self.agent_status_dao = Mock()
        self.step = UpdateAgentStatusStep(self.agent_status_dao)
        self.command = Mock()
        self.response = Mock()
        self.response.error = None
        self.blackboard = Mock()
        self.agent = Mock()
        self.agent.id = 42
        self.agent.number = '2'
        self.queue = Mock()
        self.queue.id = 10
        self.agent.queues = [self.queue]
        self.blackboard.agent = self.agent
        self.blackboard.queue = self.queue
        self.blackboard.extension = '1001'
        self.blackboard.context = 'default'
        self.blackboard.interface = 'Local/2@foobar'
        self.blackboard.state_interface = 'SIP/abcdef'

    def test_execute_login_command(self):
        self.command.name = commands.LoginCommand.name

        self.step.execute(self.command, self.response, self.blackboard)

        self.agent_status_dao.log_in_agent.assert_called_once_with(self.agent.id,
                                                                   self.agent.number,
                                                                   self.blackboard.extension,
                                                                   self.blackboard.context,
                                                                   self.blackboard.interface,
                                                                   self.blackboard.state_interface)
        self.agent_status_dao.add_agent_to_queues.assert_called_once_with(self.agent.id,
                                                                          self.agent.queues)

    def test_execute_logoff_command(self):
        self.command.name = commands.LogoffCommand.name

        self.step.execute(self.command, self.response, self.blackboard)

        self.agent_status_dao.log_off_agent.assert_called_once_with(self.agent.id)
        self.agent_status_dao.remove_agent_from_all_queues.assert_called_once_with(self.agent.id)

    def test_execute_add_to_queue_command_with_logged_agent(self):
        self.command.name = commands.AddToQueueCommand.name

        self.step.execute(self.command, self.response, self.blackboard)

        self.agent_status_dao.add_agent_to_queues.assert_called_once_with(self.agent.id, [self.queue])

    def test_execute_add_to_queue_command_with_unlogged_agent(self):
        self.command.name = commands.AddToQueueCommand.name
        self.blackboard.agent_status = None

        self.step.execute(self.command, self.response, self.blackboard)

        self.assertFalse(self.agent_status_dao.add_agent_to_queues.called)

    def test_execute_remove_from_queue_command_with_logged_agent(self):
        self.command.name = commands.RemoveFromQueueCommand.name

        self.step.execute(self.command, self.response, self.blackboard)

        self.agent_status_dao.remove_agent_from_queues.assert_called_once_with(self.agent.id, [self.queue.id])

    def test_execute_remove_from_queue_command_with_unlogged_agent(self):
        self.command.name = commands.RemoveFromQueueCommand.name
        self.blackboard.agent_status = None

        self.step.execute(self.command, self.response, self.blackboard)

        self.assertFalse(self.agent_status_dao.remove_agent_from_queues.called)
