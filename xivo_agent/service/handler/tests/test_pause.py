# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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
from xivo_agent.service.manager.pause import PauseManager
from xivo_agent.service.handler.pause import PauseHandler


class TestPauseHandler(unittest.TestCase):

    def setUp(self):
        self.pause_manager = Mock(PauseManager)
        self.agent_status_dao = Mock()
        self.pause_handler = PauseHandler(self.pause_manager, self.agent_status_dao)

    def test_pause_by_number(self):
        agent_number = '42'
        agent_status = Mock()
        self.agent_status_dao.get_status_by_number.return_value = agent_status

        self.pause_handler.handle_pause_by_number(agent_number)

        self.agent_status_dao.get_status_by_number.assert_called_once_with(agent_number)
        self.pause_manager.pause_agent.assert_called_once_with(agent_status)

    def test_unpause_by_number(self):
        agent_number = '42'
        agent_status = Mock()
        self.agent_status_dao.get_status_by_number.return_value = agent_status

        self.pause_handler.handle_unpause_by_number(agent_number)

        self.agent_status_dao.get_status_by_number.assert_called_once_with(agent_number)
        self.pause_manager.unpause_agent.assert_called_once_with(agent_status)
