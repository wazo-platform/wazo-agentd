# Copyright 2013-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock

from wazo_agentd.service.manager.logoff import LogoffManager


class TestLogoffManager(unittest.TestCase):
    def setUp(self):
        self.logoff_action = Mock()
        self.agent_dao = Mock()
        self.agent_status_dao = Mock()
        self.logoff_manager = LogoffManager(
            self.logoff_action, self.agent_dao, self.agent_status_dao
        )

    def test_logoff_agent(self):
        agent_status = Mock()

        self.logoff_manager.logoff_agent(agent_status)

        self.logoff_action.logoff_agent.assert_called_once_with(agent_status)

    def test_logoff_user_agent(self):
        agent_status = Mock()
        self.agent_dao.agent_with_user_uuid.return_value = Mock()

        self.logoff_manager.logoff_agent(agent_status)

        self.logoff_action.logoff_agent.assert_called_once_with(agent_status)
