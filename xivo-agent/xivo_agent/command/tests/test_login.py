# -*- coding: utf-8 -*-

# Copyright (C) 2012-2013 Avencall
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

from __future__ import unicode_literals

import unittest
from xivo_agent.command.login import LoginByIDCommand, LoginByNumberCommand


class TestLoginCommand(unittest.TestCase):

    def setUp(self):
        self.agent_id = 1
        self.agent_number = '1'
        self.extension = '1001'
        self.context = 'default'
        self.by_id_msg = {'agent_id': self.agent_id, 'extension': self.extension, 'context': self.context}
        self.by_number_msg = {'agent_number': self.agent_number, 'extension': self.extension, 'context': self.context}

    def test_marshal_by_id(self):
        command = LoginByIDCommand(self.agent_id, self.extension, self.context)

        msg = command.marshal()

        self.assertEqual(msg, self.by_id_msg)

    def test_unmarshal_by_id(self):
        command = LoginByIDCommand.unmarshal(self.by_id_msg)

        self.assertEqual(command.name, LoginByIDCommand.name)
        self.assertEqual(command.agent_id, self.agent_id)
        self.assertEqual(command.extension, self.extension)
        self.assertEqual(command.context, self.context)

    def test_marshal_by_number(self):
        command = LoginByNumberCommand(self.agent_number, self.extension, self.context)

        msg = command.marshal()

        self.assertEqual(msg, self.by_number_msg)

    def test_unmarshal_by_number(self):
        command = LoginByNumberCommand.unmarshal(self.by_number_msg)

        self.assertEqual(command.name, LoginByNumberCommand.name)
        self.assertEqual(command.agent_number, self.agent_number)
        self.assertEqual(command.extension, self.extension)
        self.assertEqual(command.context, self.context)
