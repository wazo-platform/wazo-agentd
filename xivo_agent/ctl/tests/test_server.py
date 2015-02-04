# -*- coding: utf-8 -*-

# Copyright (C) 2012-2015 Avencall
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

from mock import Mock, patch

from ..server import AgentServer
from xivo_agent.exception import AgentServerError
from xivo_bus.ctl.rpc.response import CommandResponse
from xivo_bus.ctl.marshaler import Marshaler


class TestAgentServer(unittest.TestCase):

    @patch('xivo_bus.ctl.rpc.amqp_transport.AMQPTransportServer.create_and_connect', Mock())
    def test_command_callback_is_called_by_process_next_command(self):
        callback = Mock()
        marshaler = Mock()

        server = AgentServer()
        server._marshaler = marshaler

        command = Mock()
        command.name = "foobar"
        marshaler.unmarshal_command.return_value = command

        command_class = Mock()
        command_class.name = "foobar"

        server.add_command(command_class, callback)

        server._process_next_command('{"name": "foobar", "arg": {"arg1": "value"}}')

        callback.assert_called_once_with(command)

    @patch('xivo_bus.ctl.rpc.amqp_transport.AMQPTransportServer.create_and_connect', Mock())
    @patch('xivo_agent.ctl.server.CommandResponse')
    def test_server_sends_marshaled_exception_when_callback_raises_exception(self, mock_command_response):
        request = '{"name": "foobar", "arg": {"arg1": "value"}}'

        expected = '{"error": "raise me!", "value": null}'

        command_response = Mock(CommandResponse)
        command_response.error = "raise me!"
        command_response.value = None
        mock_command_response.return_value = command_response
        callback = Mock(side_effect=AgentServerError())

        marshaler = Mock(Marshaler)
        server = AgentServer()
        server._marshaler = marshaler

        command = Mock()
        command.name = "foobar"
        marshaler.unmarshal_command.return_value = command
        marshaler.marshal_response.return_value = expected

        command_class = Mock()
        command_class.name = "foobar"

        server.add_command(command_class, callback)

        response = server._process_next_command(request)

        self.assertEqual(response, expected)
        marshaler.marshal_response.assert_called_once_with(command_response)
