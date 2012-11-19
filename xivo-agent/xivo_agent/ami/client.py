# -*- coding: UTF-8 -*-

import collections
import logging
import socket
from xivo_agent.ami.event import Event
from xivo_agent.ami.response import Response
from xivo_agent.ami.parser import parse_msg

logger = logging.getLogger(__name__)


def _action_id_generator():
    n = 0
    while True:
        yield str(n)
        n += 1


class AMIClient(object):

    _BUFSIZE = 4096
    _TIMEOUT = 10

    def __init__(self):
        self._sock = None
        self._new_action_id = _action_id_generator().next
        self._action_ids = {}
        self._buffer = ''
        self._msgs_queue = collections.deque()

    def close(self):
        if self._sock is None:
            return

        logger.info('Disconnecting AMI client')
        self._sock.close()
        self._sock = None

    def connect(self, hostname, port):
        if self._sock is not None:
            raise Exception('already connected')

        logger.info('Connecting AMI client to %s:%s', hostname, port)
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(self._TIMEOUT)
        self._sock.connect((hostname, port))
        # discard the AMI protocol version
        self._sock.recv(self._BUFSIZE)

    def execute(self, action):
        action._action_id = self._new_action_id()
        self._send_action(action)

    def _send_action(self, action):
        data = action.format()
        self._sock.sendall(data)
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
            self._recv_data()
            self._parse_next_msgs()
        self._process_msgs_queue()

    def _recv_data(self):
        data = self._sock.recv(self._BUFSIZE)
        if not data:
            raise Exception('remote connection closed')
        self._buffer += data

    def _parse_next_msgs(self):
        while True:
            head, sep, self._buffer = self._buffer.partition('\r\n\r\n')
            if not sep:
                self._buffer = head
                break

            try:
                msg = parse_msg(head)
            except Exception as e:
                logger.error('Could not parse message: %s', e)
                continue
            self._msgs_queue.append(msg)

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
