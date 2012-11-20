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

import json
import logging
from xivo_agent.ctl.response import CommandResponse

logger = logging.getLogger(__name__)


class Transport(object):

    _BUFSIZE = 2048

    def __init__(self, sock):
        self._sock = sock

    def close(self):
        self._sock.close()

    def send_command(self, command, addr):
        data = self._marshal_command(command)
        self._sock.sendto(data, addr)

    def send_response(self, response, addr):
        data = self._marshal_response(response)
        self._sock.sendto(data, addr)

    def recv_command(self, command_registry):
        data, addr = self._sock.recvfrom(self._BUFSIZE)
        try:
            command = self._unmarshal_command(data, command_registry)
        except Exception:
            logger.warning('Could not unmarshal command:', exc_info=True)
            self._send_error_response(CommandResponse.ERR_CLIENT, addr)
            return None, None
        else:
            return command, addr

    def recv_response(self):
        data, _ = self._sock.recvfrom(self._BUFSIZE)
        response = self._unmarshal_response(data)
        return response

    def _marshal_command(self, command):
        return json.dumps({'name': command.name, 'cmd': command.marshal()})

    def _marshal_response(self, response):
        return json.dumps(response.marshal())

    def _unmarshal_command(self, data, command_registry):
        msg = json.loads(data)
        msg_name = msg['name']
        msg_cmd = msg['cmd']
        cmd_class = command_registry[msg_name]
        return cmd_class.unmarshal(msg_cmd)

    def _unmarshal_response(self, data):
        msg = json.loads(data)
        return CommandResponse.unmarshal(msg)

    def _send_error_response(self, error, addr):
        self.send_response(CommandResponse(error=error), addr)
