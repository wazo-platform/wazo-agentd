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
from xivo_agent.ami.client import AMIClient
from xivo_agent.ami.response import Response


class TestAMIClient(unittest.TestCase):

    def setUp(self):
        self.hostname = 'example.org'
        self.port = 5038
        self.ami_client = AMIClient(self.hostname, self.port)

    def _new_mocked_amiclient(self, action_id, lines):
        ami_client = AMIClient(self.hostname, self.port)
        ami_client._new_action_id = Mock()
        ami_client._new_action_id.return_value = action_id
        ami_client._sock = Mock()
        ami_client._sock.recv.return_value = '\r\n'.join(lines) + '\r\n'
        return ami_client

    def test_sock_is_none_after_init(self):
        self.assertEqual(None, self.ami_client._sock)

    def test_disconnect_can_be_called_after_init(self):
        self.ami_client.disconnect()

    def test_disconnect_can_be_called_multiple_times(self):
        self.ami_client.disconnect()
        self.ami_client.disconnect()

    def test_execute(self):
        ami_client = self._new_mocked_amiclient('foo', [
            'Response: Success',
            'ActionID: foo',
            '',
        ])
        action = Mock()
        action._completed = False
        action._on_response_received.side_effect = lambda _: setattr(action, '_completed', True)

        ami_client.execute(action)

        self.assertEqual(ami_client, action._amiclient)
        self.assertEqual('foo', action._action_id)
        action.format.assert_called_once_with()
        self.assertEqual({'foo': action}, ami_client._action_ids)

    def test_add_data_to_buffer(self):
        ami_client = self._new_mocked_amiclient(None, [
            'Response: Success',
            ''
        ])

        ami_client._add_data_to_buffer()

        self.assertEqual('Response: Success\r\n\r\n', ami_client._buffer)

    def test_parse_next_msgs(self):
        self.ami_client._buffer = 'Response: Success\r\n\r\n'

        self.ami_client._parse_next_msgs()

        self.assertEqual(1, len(self.ami_client._msgs_queue))
        self.assertEqual('Success', self.ami_client._msgs_queue[0].response)

    def test_process_msgs_queue(self):
        action = Mock()
        response = Response('Success', 'foobar', {})
        self.ami_client._msgs_queue.append(response)
        self.ami_client._action_ids = {'foobar': action}

        self.ami_client._process_msgs_queue()

        self.assertFalse(self.ami_client._msgs_queue)
        action._on_response_received.assert_called_once_with(response)
