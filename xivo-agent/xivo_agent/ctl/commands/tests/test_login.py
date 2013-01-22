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
from xivo_agent.ctl.commands import LoginCommand


class TestLoginCommand(unittest.TestCase):

    def setUp(self):
        self.agent_id = 1
        self.agent_number = '2'
        self.extension = '123'
        self.context = 'foo'

    def test_marshal_by_id(self):
        command = LoginCommand(self.extension, self.context).by_id(self.agent_id)

        msg = command.marshal()

        expected_msg = {
            'agent_id': self.agent_id,
            'agent_number': None,
            'extension': self.extension,
            'context': self.context,
        }
        self.assertEqual(msg, expected_msg)

    def test_marshal_by_number(self):
        command = LoginCommand(self.extension, self.context).by_number(self.agent_number)

        msg = command.marshal()

        expected_msg = {
            'agent_id': None,
            'agent_number': self.agent_number,
            'extension': self.extension,
            'context': self.context,
        }
        self.assertEqual(msg, expected_msg)

    def test_unmarshal_by_id(self):
        msg = {
            'agent_id': self.agent_id,
            'agent_number': None,
            'extension': self.extension,
            'context': self.context,
        }

        command = LoginCommand.unmarshal(msg)

        self.assertEqual(command.agent_id, self.agent_id)
        self.assertEqual(command.agent_number, None)
        self.assertEqual(command.extension, self.extension)
        self.assertEqual(command.context, self.context)

    def test_unmarshal_by_number(self):
        msg = {
            'agent_id': None,
            'agent_number': self.agent_number,
            'extension': self.extension,
            'context': self.context,
        }

        command = LoginCommand.unmarshal(msg)

        self.assertEqual(command.agent_id, None)
        self.assertEqual(command.agent_number, self.agent_number)
        self.assertEqual(command.extension, self.extension)
        self.assertEqual(command.context, self.context)
