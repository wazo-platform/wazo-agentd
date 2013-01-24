# -*- coding: utf-8 -*-

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
from xivo_agent.service.handler.logoff import LogoffHandler
from xivo_agent.service.manager.logoff import LogoffManager


class TestLogoffHandler(unittest.TestCase):

    def setUp(self):
        self.logoff_manager = Mock(LogoffManager)
        self.agent_status_dao = Mock()
        self.logoff_handler = LogoffHandler(self.logoff_manager, self.agent_status_dao)

    def test_handle_logoff_by_id(self):
        agent_id = 10
        agent_status = Mock()
        command = Mock()
        command.agent_id = agent_id
        self.agent_status_dao.get_status.return_value = agent_status

        self.logoff_handler.handle_logoff_by_id(command)

        self.agent_status_dao.get_status.assert_called_once_with(agent_id)
        self.logoff_manager.logoff_agent.assert_called_once_with(agent_status)

    def test_handle_logoff_by_number(self):
        agent_number = '10'
        agent_status = Mock()
        command = Mock()
        command.agent_number = agent_number
        self.agent_status_dao.get_status_by_number.return_value = agent_status

        self.logoff_handler.handle_logoff_by_number(command)

        self.agent_status_dao.get_status_by_number.assert_called_once_with(agent_number)
        self.logoff_manager.logoff_agent.assert_called_once_with(agent_status)
