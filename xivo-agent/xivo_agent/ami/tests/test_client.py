# -*- coding: UTF-8 -*-

import unittest
from mock import Mock
from xivo_agent.ami.client import AMIClient
from xivo_agent.ami.response import Response


class TestAMIClient(unittest.TestCase):

    def _new_mocked_amiclient(self, action_id, lines):
        amiclient = AMIClient()
        amiclient._new_action_id = Mock()
        amiclient._new_action_id.return_value = action_id
        amiclient._sock = Mock()
        amiclient._sock.recv.return_value = '\r\n'.join(lines) + '\r\n'
        return amiclient

    def test_sock_is_none_after_init(self):
        amiclient = AMIClient()

        self.assertEqual(None, amiclient._sock)

    def test_close_can_be_called_after_init(self):
        amiclient = AMIClient()
        amiclient.close()

    def test_execute(self):
        amiclient = self._new_mocked_amiclient('foo', [
            'Response: Success',
            'ActionID: foo',
            '',
        ])
        action = Mock()
        action._completed = False
        action._on_response_received.side_effect = lambda _: setattr(action, '_completed', True)

        amiclient.execute(action)

        self.assertEqual(amiclient, action._amiclient)
        self.assertEqual('foo', action._action_id)
        action.format.assert_called_once_with()
        self.assertEqual({'foo': action}, amiclient._action_ids)

    def test_recv_data(self):
        amiclient = self._new_mocked_amiclient(None, [
            'Response: Success',
            ''
        ])

        amiclient._recv_data()

        self.assertEqual('Response: Success\r\n\r\n', amiclient._buffer)

    def test_parse_next_msgs(self):
        amiclient = self._new_mocked_amiclient(None, [])
        amiclient._buffer = 'Response: Success\r\n\r\n'

        amiclient._parse_next_msgs()

        self.assertEqual(1, len(amiclient._msgs_queue))
        self.assertEqual('Success', amiclient._msgs_queue[0].response)

    def test_process_msgs_queue(self):
        action = Mock()
        response = Response('Success', 'foobar', {})
        amiclient = AMIClient()
        amiclient._msgs_queue.append(response)
        amiclient._action_ids = {'foobar': action}

        amiclient._process_msgs_queue()

        self.assertFalse(amiclient._msgs_queue)
        action._on_response_received.assert_called_once_with(response)
