# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

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
