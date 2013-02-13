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
from xivo_agent.service.action.pause import PauseAction


class TestPauseAction(unittest.TestCase):

    def setUp(self):
        self.ami_client = Mock()
        self.pause_action = PauseAction(self.ami_client)

    def test_pause_agent(self):
        agent_status = Mock()

        self.pause_action.pause_agent(agent_status)

        self.ami_client.queue_pause.assert_called_once_with(agent_status.interface, '1')

    def test_unpause_agent(self):
        agent_status = Mock()

        self.pause_action.unpause_agent(agent_status)

        self.ami_client.queue_pause.assert_called_once_with(agent_status.interface, '0')
