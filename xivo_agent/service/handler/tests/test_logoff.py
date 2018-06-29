# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

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
        self.agent_status_dao.get_status.return_value = agent_status

        self.logoff_handler.handle_logoff_by_id(agent_id)

        self.agent_status_dao.get_status.assert_called_once_with(agent_id)
        self.logoff_manager.logoff_agent.assert_called_once_with(agent_status)

    def test_handle_logoff_by_number(self):
        agent_number = '10'
        agent_status = Mock()
        self.agent_status_dao.get_status_by_number.return_value = agent_status

        self.logoff_handler.handle_logoff_by_number(agent_number)

        self.agent_status_dao.get_status_by_number.assert_called_once_with(agent_number)
        self.logoff_manager.logoff_agent.assert_called_once_with(agent_status)
