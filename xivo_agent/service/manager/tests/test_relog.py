# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from mock import Mock
from xivo_agent.service.action.login import LoginAction
from xivo_agent.service.action.logoff import LogoffAction
from xivo_agent.service.manager.relog import RelogManager


class TestRelogManager(unittest.TestCase):

    def setUp(self):
        self.login_action = Mock(LoginAction)
        self.logoff_action = Mock(LogoffAction)
        self.agent_status_dao = Mock()
        self.agent_dao = Mock()
        self.relog_manager = RelogManager(self.login_action, self.logoff_action,
                                          self.agent_dao, self.agent_status_dao)

    def test_relog_all_agents(self):
        agent_id = 42
        agent = Mock()
        agent_status = Mock()
        agent_status.agent_id = agent_id

        self.agent_dao.get_agent.return_value = agent
        self.agent_status_dao.get_logged_agent_ids.return_value = [agent_id]
        self.agent_status_dao.get_status.return_value = agent_status

        self.relog_manager.relog_all_agents()

        self.agent_status_dao.get_status.assert_called_once_with(agent_id)
        self.logoff_action.logoff_agent.assert_called_once_with(agent_status)
        self.agent_dao.get_agent.assert_called_once_with(agent_id)
        self.login_action.login_agent.assert_called_once_with(agent, agent_status.extension, agent_status.context)
