# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

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
        reason = Mock()
        self.agent_status_dao.get_status_by_number.return_value = agent_status

        self.pause_handler.handle_pause_by_number(agent_number, reason)

        self.agent_status_dao.get_status_by_number.assert_called_once_with(agent_number)
        self.pause_manager.pause_agent.assert_called_once_with(agent_status, reason)

    def test_unpause_by_number(self):
        agent_number = '42'
        agent_status = Mock()
        self.agent_status_dao.get_status_by_number.return_value = agent_status

        self.pause_handler.handle_unpause_by_number(agent_number)

        self.agent_status_dao.get_status_by_number.assert_called_once_with(agent_number)
        self.pause_manager.unpause_agent.assert_called_once_with(agent_status)
