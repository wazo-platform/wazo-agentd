# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from mock import Mock
from xivo_agent.service.manager.relog import RelogManager
from xivo_agent.service.handler.relog import RelogHandler


class TestRelogHandler(unittest.TestCase):

    def setUp(self):
        self.relog_manager = Mock(RelogManager)
        self.agent_status_dao = Mock()
        self.relog_handler = RelogHandler(self.relog_manager)

    def test_handle_relog_all(self):
        self.relog_handler.handle_relog_all()

        self.relog_manager.relog_all_agents.assert_called_once_with()
