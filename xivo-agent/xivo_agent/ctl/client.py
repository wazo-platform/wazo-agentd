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

import socket
from xivo_agent.ctl.server import AgentServer
from xivo_agent.ctl.commands import LoginCommand, LogoffCommand, StatusCommand
from xivo_agent.ctl.transport import Transport
from xivo_agent.exception import AgentClientError


class AgentClient(object):

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

        self._addr = (hostname, AgentServer.PORT)
        self._transport = Transport(self._new_socket())

    def _new_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(self._TIMEOUT)
        sock.connect(self._addr)
        return sock

    def login_agent(self, agent_id, extension, context):
        cmd = LoginCommand(extension, context).by_id(agent_id)
        return self._execute_command(cmd)

    def login_agent_by_number(self, agent_number, extension, context):
        cmd = LoginCommand(extension, context).by_number(agent_number)
        return self._execute_command(cmd)

    def logoff_agent(self, agent_id):
        cmd = LogoffCommand().by_id(agent_id)
        return self._execute_command(cmd)

    def logoff_agent_by_number(self, agent_number):
        cmd = LogoffCommand().by_number(agent_number)
        return self._execute_command(cmd)

    def get_agent_status(self, agent_id):
        cmd = StatusCommand().by_id(agent_id)
        return self._execute_command(cmd)

    def get_agent_status_by_number(self, agent_number):
        cmd = StatusCommand().by_number(agent_number)
        return self._execute_command(cmd)

    def _execute_command(self, cmd):
        self._send_command(cmd)
        return self._recv_response()

    def _send_command(self, cmd):
        self._transport.send_command(cmd, self._addr)

    def _recv_response(self):
        response = self._transport.recv_response()
        if response.error is not None:
            raise AgentClientError(response.error)
        return response.value
