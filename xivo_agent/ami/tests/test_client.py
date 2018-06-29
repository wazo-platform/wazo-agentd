# -*- coding: utf-8 -*-
# Copyright (C) 2012-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import socket
import unittest
from mock import Mock, patch
from xivo_agent.ami.client import AMIClient, ReconnectingAMIClient
from xivo_agent.ami.response import Response


class TestAMIClient(unittest.TestCase):

    def setUp(self):
        self.hostname = 'example.org'
        self.port = 5038
        self.on_connect_callback = Mock()
        self.ami_client = AMIClient(self.hostname, self.port, self.on_connect_callback)

    def _new_mocked_amiclient(self, action_id, lines):
        ami_client = AMIClient(self.hostname, self.port, self.on_connect_callback)
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

    @patch('socket.socket')
    def test_execute_connect_socket_if_not_connected(self, socket_mock):
        action = Mock()

        self.ami_client.execute(action)

        socket_mock.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
        self.assertNotEqual(None, self.ami_client._sock)

    @patch('socket.socket')
    def test_execute_dont_connect_socket_if_connected(self, socket_mock):
        action = Mock()
        self.ami_client._sock = Mock()

        self.ami_client.execute(action)

        self.assertFalse(socket_mock.called)

    def test_add_data_to_buffer(self):
        ami_client = self._new_mocked_amiclient(None, [
            'Response: Success',
            ''
        ])

        ami_client._add_data_to_buffer()

        self.assertEqual('Response: Success\r\n\r\n', ami_client._buffer)

    def test_process_msgs_queue(self):
        action = Mock()
        response = Response('Success', 'foobar', {})
        self.ami_client._msgs_queue.append(response)
        self.ami_client._action_ids = {'foobar': action}

        self.ami_client._process_msgs_queue()

        self.assertFalse(self.ami_client._msgs_queue)
        action._on_response_received.assert_called_once_with(response)

    def test_given_response_when_parse_next_msgs_then_response_msg_added_to_queue(self):
        self.ami_client._buffer = 'Response: Success\r\nMessage: bar\r\n\r\n'

        self.ami_client._parse_next_msgs()

        self.assertEqual(1, len(self.ami_client._msgs_queue))
        self.assertEqual('Success', self.ami_client._msgs_queue[0].response)
        self.assertEqual(None, self.ami_client._msgs_queue[0].action_id)
        self.assertTrue(self.ami_client._msgs_queue[0].is_success())

    def test_given_event_with_action_id_when_parse_next_msgs_then_event_msg_added_to_queue(self):
        self.ami_client._buffer = 'Event: Foo\r\nActionID: bar\r\n\r\n'

        self.ami_client._parse_next_msgs()

        self.assertEqual(1, len(self.ami_client._msgs_queue))
        self.assertEqual('Foo', self.ami_client._msgs_queue[0].name)
        self.assertEqual('bar', self.ami_client._msgs_queue[0].action_id)


class TestReconnectingAMIClient(unittest.TestCase):

    def setUp(self):
        self.sock = Mock()
        self.on_connect_callback = Mock()
        self.ami_client = ReconnectingAMIClient('example.org', 5038, self.on_connect_callback)
        self.ami_client._sock = self.sock

    @patch('socket.socket')
    def test_on_recv_socket_no_data_and_reconnection_ok(self, socket_mock):
        action = Mock()
        action_ids = {'1': action}
        self.ami_client._action_ids = dict(action_ids)
        self.ami_client._buffer = 'foobar'
        self.sock.recv.return_value = ''

        data = self.ami_client._recv_data_from_socket()

        self.assertTrue(socket_mock.called)
        self.on_connect_callback.assert_called_once_with()
        self.assertEqual('', self.ami_client._buffer)
        self.assertEqual(action_ids, self.ami_client._action_ids)
        self.assertEqual('', data)

    @patch('socket.socket')
    def test_on_send_socket_error_and_reconnection_ok(self, socket_mock):
        action = Mock()
        action_ids = {'1': action}
        self.ami_client._action_ids = dict(action_ids)
        self.ami_client._buffer = 'foobar'
        self.sock.sendall.side_effect = socket.error('test')

        self.ami_client._send_data_to_socket('42 x 42')

        self.assertTrue(socket_mock.called)
        self.on_connect_callback.assert_called_once_with()
        self.assertEqual('', self.ami_client._buffer)
        self.assertEqual(action_ids, self.ami_client._action_ids)
