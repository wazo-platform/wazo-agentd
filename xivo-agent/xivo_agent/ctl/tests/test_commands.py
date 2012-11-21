# -*- coding: UTF-8 -*-

# Copyright (C) 2012  Avencall
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
from xivo_agent.ctl.commands import LoginCommand


class TestCommands(unittest.TestCase):

    def test_marshal_unmarshal_login(self):
        agent_id = 1
        extension = '123'
        context = 'foo'
        expected = {'id': agent_id, 'extension': extension, 'context': context}

        data = LoginCommand(agent_id, extension, context).marshal()

        self.assertEqual(expected, data)

        cmd = LoginCommand.unmarshal(data)

        self.assertEqual(cmd.agent_id, agent_id)
        self.assertEqual(cmd.extension, extension)
        self.assertEqual(cmd.context, context)
