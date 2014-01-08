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
from xivo_agent.service.manager.logoff import LogoffManager


class TestLogoffManager(unittest.TestCase):

    def setUp(self):
        self.logoff_action = Mock()
        self.agent_status_dao = Mock()
        self.logoff_manager = LogoffManager(self.logoff_action, self.agent_status_dao)

    def test_logoff_agent(self):
        agent_status = Mock()

        self.logoff_manager.logoff_agent(agent_status)

        self.logoff_action.logoff_agent.assert_called_once_with(agent_status)
