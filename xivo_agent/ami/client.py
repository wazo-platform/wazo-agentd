# -*- coding: utf-8 -*-
# Copyright (C) 2012-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import collections
import logging
import socket
from xivo_agent.ami.event import Event
from xivo_agent.ami.response import Response
from xivo_ami.ami.parser import parse_buffer

logger = logging.getLogger(__name__)


class AMIClient(object):

    _BUFSIZE = 4096
    _TIMEOUT = 10

    def __init__(self, hostname, port, on_connect_callback):
        self._hostname = hostname
        self._port = port
        self._on_connect_callback = on_connect_callback
        self._sock = None
        self._new_action_id = _action_id_generator().next
        self._msgs_queue = collections.deque()
        self._action_ids = {}
        self._buffer = ''

    def connect(self):
        if self._sock is None:
            self._connect_socket()

    def disconnect(self):
        if self._sock is not None:
            self._disconnect_socket()

    def execute(self, action):
        self.connect()
        action._action_id = self._new_action_id()
        self._send_action(action)

    def _send_action(self, action):
        data = action.format()
        self._send_data_to_socket(data)
        if action._action_id is None:
            action._completed = True
        else:
            action._amiclient = self
            self._action_ids[action._action_id] = action

    def wait_for_completion(self, action):
        if action._amiclient is not self:
            raise Exception('action has been executed by %r' % action._amiclient)

        while not action._completed:
            self._process_msgs()

    def _process_msgs(self):
        if not self._msgs_queue:
            self._add_data_to_buffer()
            self._parse_next_msgs()
        self._process_msgs_queue()

    def _add_data_to_buffer(self):
        data = self._recv_data_from_socket()
        self._buffer += data

    def event_callback(self, event_name, action_id, headers):
        message = Event(event_name, action_id, headers)
        self._msgs_queue.append(message)

    def response_callback(self, response, action_id, headers):
        message = Response(response, action_id, headers)
        self._msgs_queue.append(message)

    def _parse_next_msgs(self):
        self._buffer = parse_buffer(self._buffer, self.event_callback, self.response_callback)

    def _process_msgs_queue(self):
        while self._msgs_queue:
            msg = self._msgs_queue.popleft()
            if msg.action_id in self._action_ids:
                action = self._action_ids[msg.action_id]
                if msg.msg_type == Response.msg_type:
                    action._response = msg
                    action._on_response_received(msg)
                elif msg.msg_type == Event.msg_type:
                    action._on_event_received(msg)
                else:
                    raise AssertionError('unexpected msg type: %r' % msg.msg_type)
                if action._completed:
                    del self._action_ids[msg.action_id]

    def _connect_socket(self):
        logger.info('Connecting AMI client to %s:%s', self._hostname, self._port)
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(self._TIMEOUT)
        self._sock.connect((self._hostname, self._port))
        # discard the AMI protocol version
        self._sock.recv(self._BUFSIZE)
        self._on_connect_callback()

    def _disconnect_socket(self):
        logger.info('Disconnecting AMI client')
        self._sock.close()
        self._sock = None
        self._buffer = ''

    def _send_data_to_socket(self, data):
        self._sock.sendall(data)

    def _recv_data_from_socket(self):
        data = self._sock.recv(self._BUFSIZE)
        if not data:
            raise Exception('remote connection closed')
        return data


class ReconnectingAMIClient(AMIClient):

    def __init__(self, hostname, port, on_connect_callback):
        AMIClient.__init__(self, hostname, port, on_connect_callback)
        self._try_reconnection = True

    def _send_data_to_socket(self, data):
        try:
            self._sock.sendall(data)
        except socket.error as e:
            logger.error('Could not write data to socket: %s', e)
            self._reconnect()
            self._sock.sendall(data)

    def _recv_data_from_socket(self):
        try:
            data = self._sock.recv(self._BUFSIZE)
        except socket.error as e:
            logger.error('Could not read data from socket: %s', e)
            self._reconnect()
            return ''
        else:
            if not data:
                logger.error('Could not read data from socket: remote connection closed')
                self._reconnect()
                return ''
            return data

    def _reconnect(self):
        if not self._try_reconnection:
            raise ReconnectionFailedError('flag is cleared')

        self._try_reconnection = False
        try:
            self._do_reconnect()
        finally:
            self._try_reconnection = True

    def _do_reconnect(self):
        self._process_msgs_queue()
        self._disconnect_socket()
        self._connect_socket()
        for action in self._action_ids.itervalues():
            data = action.format()
            self._send_data_to_socket(data)


def _action_id_generator():
    n = 0
    while True:
        yield str(n)
        n += 1


class ReconnectionFailedError(Exception):
    pass
