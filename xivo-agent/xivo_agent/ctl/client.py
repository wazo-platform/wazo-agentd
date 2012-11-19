# -*- coding: UTF-8 -*-

import socket
from xivo_agent.ctl.server import Server
from xivo_agent.ctl.commands import LoginCommand, LogoffCommand, StatusCommand
from xivo_agent.ctl.transport import Transport
from xivo_agent.exception import AgentError


class Client(object):

    _TIMEOUT = 10

    def __init__(self):
        self._transport = None
        self._addr = None

    def close(self):
        if self._transport is None:
            return

        self._transport.close()
        self._transport = None

    def connect(self, hostname):
        if self._transport is not None:
            raise Exception('already connected')

        self._addr = (hostname, Server.PORT)
        self._transport = Transport(self._new_socket())

    def _new_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(self._TIMEOUT)
        sock.connect(self._addr)
        return sock

    def login_agent(self, agent_number, interface):
        cmd = LoginCommand(agent_number, interface)
        return self._execute_command(cmd)

    def logoff_agent(self, agent_number):
        cmd = LogoffCommand(agent_number)
        return self._execute_command(cmd)

    def get_agent_status(self, agent_number):
        cmd = StatusCommand(agent_number)
        return self._execute_command(cmd)

    def _execute_command(self, cmd):
        self._send_command(cmd)
        return self._recv_response()

    def _send_command(self, cmd):
        self._transport.send_command(cmd, self._addr)

    def _recv_response(self):
        response = self._transport.recv_response()
        if response.error is not None:
            raise AgentError(response.error)
        return response.value
