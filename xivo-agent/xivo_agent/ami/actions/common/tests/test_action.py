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
from mock import Mock
from xivo_agent.ami.actions.common.action import BaseAction


class TestBaseAction(unittest.TestCase):

    def test_new_action(self):
        action = self._new_action()

        self.assertFalse(action._completed)

    def test_wait_for_completion(self):
        action = self._new_action()
        action._amiclient = Mock()

        action.wait_for_completion()

        action._amiclient.wait_for_completion.assert_called_once_with(action)

    def test_format_with_no_action_id(self):
        action = self._new_action('Foo', [('Bar', '1')])

        data = action.format()

        self.assertEqual('Action: Foo\r\nBar: 1\r\n\r\n', data)

    def test_format_with_action_id(self):
        action = self._new_action('Foo', [('Bar', '1')])
        action._action_id = '99'

        data = action.format()

        self.assertEqual('Action: Foo\r\nActionID: 99\r\nBar: 1\r\n\r\n', data)

    def test_format_with_none_value(self):
        action = self._new_action('Foo', [('H1', None), ('H2', 0)])

        data = action.format()

        self.assertEqual('Action: Foo\r\nH2: 0\r\n\r\n', data)

    def _new_action(self, action='Foo', headers=None):
        if headers is None:
            headers = []
        return BaseAction(action, headers)
