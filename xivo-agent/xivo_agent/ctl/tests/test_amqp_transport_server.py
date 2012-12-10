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

import pika
import unittest
import logging
import subprocess

from mock import Mock, patch, ANY
from xivo_agent.ctl.amqp_transport_server import AMQPTransportServer

def phony_callback():
    pass

class TestAMQPTransportServer(unittest.TestCase):

    AMQP_HOST = 'localhost'

    def setUp(self):
        self.patcher = patch('pika.BlockingConnection')
        self.blocking_connection = self.patcher.start()
        self.connection = Mock()
        self.channel = Mock()
        self.blocking_connection.return_value = self.connection
        self.connection.channel.return_value = self.channel

    def tearDown(self):
        self.patcher.stop()

    def test_connect(self):
        transport = self._new_transport()

        self.connection.channel.assert_called_once_with()

    def test_setup_queue(self):
        transport = self._new_transport()
        self.channel.queue_declare.assert_called_once_with(queue='xivo_agent')
        self.channel.basic_qos.assert_called_once_with(prefetch_count=1)
        self.channel.basic_consume.assert_called_once_with(ANY, 'xivo_agent')

    def test_unmarshal_command(self):
        json = '{"cmd": {"a": 1}, "name": "foobar"}'
        FoobarCommand = Mock()
        FoobarCommand.unmarshal.return_value = 'fake'

        registry = {
            'foobar': FoobarCommand
        }

        transport = self._new_transport(registry=registry)
        command = transport._unmarshal_command(json)

        FoobarCommand.unmarshal.assert_called_once_with({'a': 1})
        self.assertEqual('fake', command)

    def test_marshal_response(self):
        json = '{"value": null, "error": null}'
        response = Mock()
        response.marshal.return_value = {'error': None, 'value': None}

        transport = self._new_transport()
        result = transport._marshal_response(response)

        response.marshal.assert_called_once_with()
        self.assertEquals(result, json)

    def test_on_request(self):
        channel = Mock()
        method = Mock()
        properties = Mock()

        FoobarCommand = Mock()
        FoobarCommand.unmarshal.return_value = 'fake'

        response = Mock()
        response.marshal.return_value = {'error': None, 'value': None}

        command_callback = Mock()
        command_callback.return_value = response

        body = '{"cmd": {"a": 1}, "name": "foobar"}'

        command_registry = {
            'foobar': FoobarCommand
        }

        transport = self._new_transport(command_registry, command_callback)
        transport._on_request(channel, method, properties, body)

        FoobarCommand.unmarshal.assert_called_once_with({'a': 1})

        command_callback.assert_called_once()

        self.channel.basic_publish.assert_called_once()

        self.channel.basic_ack.assert_called_once()


    def _new_transport(self, registry={}, callback=None):
        host = 'localhost'
        params = pika.ConnectionParameters(host=host)

        if not callback:
            callback = phony_callback

        transport = AMQPTransportServer(params, registry, callback)

        return transport

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARN)
    unittest.main()