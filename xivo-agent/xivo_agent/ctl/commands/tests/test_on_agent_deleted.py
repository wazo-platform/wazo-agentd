# -*- coding: UTF-8 -*-

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
from xivo_agent.ctl.commands import OnAgentDeletedCommand


class TestOnAgentDeletedCommand(unittest.TestCase):

    def test_marshal(self):
        agent_id = 42
        command = OnAgentDeletedCommand(agent_id)

        msg = command.marshal()

        self.assertEqual(msg, {'agent_id': agent_id})

    def test_unmarshal(self):
        agent_id = 42
        msg = {'agent_id': agent_id}

        command = OnAgentDeletedCommand.unmarshal(msg)

        self.assertEqual(command.agent_id, agent_id)
