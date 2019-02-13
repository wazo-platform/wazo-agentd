# Copyright (C) 2013-2015 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from mock import Mock

from xivo_agent.service.manager.logoff import LogoffManager


class TestLogoffManager(unittest.TestCase):

    def setUp(self):
        self.logoff_action = Mock()
        self.agent_status_dao = Mock()
        self.logoff_manager = LogoffManager(self.logoff_action,
                                            self.agent_status_dao)

    def test_logoff_agent(self):
        agent_status = Mock()

        self.logoff_manager.logoff_agent(agent_status)

        self.logoff_action.logoff_agent.assert_called_once_with(agent_status)
