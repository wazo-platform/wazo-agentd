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
from xivo_agent.service.handler.login import LoginHandler
from xivo_agent.service.manager.login import LoginManager


class TestLoginHandler(unittest.TestCase):

    def setUp(self):
        self.login_manager = Mock(LoginManager)
        self.agent_dao = Mock()
        self.login_handler = LoginHandler(self.login_manager, self.agent_dao)

    def test_handle_login_by_id(self):
        agent_id = 10
        extension = '1001'
        context = 'default'
        agent = Mock()
        self.agent_dao.get_agent.return_value = agent

        self.login_handler.handle_login_by_id(agent_id, extension, context)

        self.agent_dao.get_agent.assert_called_once_with(agent_id)
        self.login_manager.login_agent.assert_called_once_with(agent, extension, context)

    def test_handle_login_by_number(self):
        agent_number = '10'
        extension = '1001'
        context = 'default'
        agent = Mock()
        self.agent_dao.get_agent_by_number.return_value = agent

        self.login_handler.handle_login_by_number(agent_number, extension, context)

        self.agent_dao.get_agent_by_number.assert_called_once_with(agent_number)
        self.login_manager.login_agent.assert_called_once_with(agent, extension, context)
