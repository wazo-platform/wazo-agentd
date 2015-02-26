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
