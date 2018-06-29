# -*- coding: utf-8 -*-
# Copyright (C) 2013-2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import Mock

from xivo_agent.service.manager.login import LoginManager


class TestLoginManager(unittest.TestCase):

    def setUp(self):
        self.login_action = Mock()
        self.agent_status_dao = Mock()
        self.login_manager = LoginManager(self.login_action,
                                          self.agent_status_dao)

    def test_login_agent(self):
        agent = Mock()
        extension = '1001'
        context = 'default'
        self.agent_status_dao.get_status.return_value = None
        self.agent_status_dao.is_extension_in_use.return_value = False

        self.login_manager.login_agent(agent, extension, context)

        self.login_action.login_agent.assert_called_once_with(agent, extension, context)
