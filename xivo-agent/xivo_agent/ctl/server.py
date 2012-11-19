# -*- coding: UTF-8 -*-

import logging
import socket
from xivo_agent.ctl.response import CommandResponse
from xivo_agent.ctl.transport import Transport

logger = logging.getLogger(__name__)


class Server(object):

    PORT = 6741

    def __init__(self):
        self._transport = None
        self._commands_registry = {}
        self._commands_callback = {}

    def close(self):
        if self._transport is None:
            return

        self._transport.close()
        self._transport = None

    def bind(self, bind_address):
        if self._transport is not None:
            raise Exception('already bound')

        self._transport = Transport(self._new_socket(bind_address))

    def _new_socket(self, bind_address):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((bind_address, self.PORT))
        return sock

    def add_command(self, cmd_class, callback):
        if cmd_class.name in self._commands_registry:
            raise Exception('command %r is already registered' % cmd_class.name)

        self._commands_registry[cmd_class.name] = cmd_class
        self._commands_callback[cmd_class.name] = callback

    def process_next_command(self):
        command, address = self._transport.recv_command(self._commands_registry)
        if command is None:
            return

        callback = self._commands_callback[command.name]
        response = CommandResponse()
        try:
            callback(command, response)
        except Exception:
            logger.warning('Error while processing cmd: %s', exc_info=True)
            self._reply_error(CommandResponse.ERR_SERVER, address)
            return

        self._reply_response(response, address)

    def _reply_error(self, error, address):
        self._reply_response(CommandResponse(error=error), address)

    def _reply_response(self, response, address):
        self._transport.send_response(response, address)
