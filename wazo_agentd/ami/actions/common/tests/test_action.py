# Copyright 2012-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from mock import Mock
from wazo_agentd.ami.actions.common.action import BaseAction


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

        self.assertEqual(b'Action: Foo\r\nBar: 1\r\n\r\n', data)

    def test_format_with_action_id(self):
        action = self._new_action('Foo', [('Bar', '1')])
        action._action_id = '99'

        data = action.format()

        self.assertEqual(b'Action: Foo\r\nActionID: 99\r\nBar: 1\r\n\r\n', data)

    def test_format_with_none_value(self):
        action = self._new_action('Foo', [('H1', None), ('H2', 0)])

        data = action.format()

        self.assertEqual(b'Action: Foo\r\nH2: 0\r\n\r\n', data)

    def _new_action(self, action='Foo', headers=None):
        if headers is None:
            headers = []
        return BaseAction(action, headers)
