# -*- coding: UTF-8 -*-

# Copyright (C) 2012-2013  Avencall
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


import logging
from xivo_agent.ctl import error
from xivo_agent.ctl.response import CommandResponse
from xivo_agent.ctl.marshaler import Marshaler
from xivo_agent.ctl.amqp_transport_server import AMQPTransportServer
from xivo_agent.exception import AgentServerError
from sqlalchemy.exc import OperationalError, InvalidRequestError

logger = logging.getLogger(__name__)


class AgentServer(object):

    _HOST = 'localhost'

    def __init__(self, db_manager):
        self._db_manager = db_manager
        self._transport = self._setup_transport()
        self._marshaler = None
        self._commands_registry = {}
        self._commands_callback = {}

    def _setup_transport(self):
        transport = AMQPTransportServer.create_and_connect(self._HOST, self._process_next_command)
        return transport

    def add_command(self, cmd_class, callback):
        if cmd_class.name in self._commands_registry:
            raise Exception('command %r is already registered' % cmd_class.name)

        self._commands_registry[cmd_class.name] = cmd_class
        self._commands_callback[cmd_class.name] = callback

    def _process_next_command(self, request):
        response = CommandResponse()
        try:
            command = self._marshaler.unmarshal_command(request)
            callback = self._commands_callback[command.name]
            self._call_callback(callback, command, response)
        except Exception:
            logger.warning('Error while processing command', exc_info=True)
            error_response = self._reply_error(error.SERVER_ERROR)
            raise AgentServerError(error_response)

        return self._reply_response(response)

    def _call_callback(self, callback, command, response):
        try:
            callback(command, response)
        except (InvalidRequestError, OperationalError) as e:
            logger.warning('Database error while processing command: %s', e)
            self._db_manager.reconnect()
            callback(command, response)

    def _reply_error(self, error):
        resp = CommandResponse(error=error)
        return self._reply_response(resp)

    def _reply_response(self, response):
        return self._marshaler.marshal_response(response)

    def run(self):
        self._marshaler = Marshaler(self._commands_registry)
        self._transport.run()

    def close(self):
        self._transport.close()
        self._transport = None
