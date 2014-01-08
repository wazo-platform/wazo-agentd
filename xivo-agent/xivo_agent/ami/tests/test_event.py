# -*- coding: utf-8 -*-

# Copyright (C) 2012-2014 Avencall
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
from xivo_agent.ami.parser import parse_msg


class TestResponse(unittest.TestCase):

    def test_parse_response(self):
        data = 'Event: foo'

        event = parse_msg(data)

        self.assertEqual('foo', event.name)
        self.assertEqual(None, event.action_id)

    def test_parse_response_with_action_id(self):
        data = 'Event: foo\r\nActionID: bar'

        event = parse_msg(data)

        self.assertEqual('foo', event.name)
        self.assertEqual('bar', event.action_id)
