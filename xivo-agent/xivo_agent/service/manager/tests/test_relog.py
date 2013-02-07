# -*- coding: utf-8 -*-

# Copyright (C) 2013  Avencall
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
