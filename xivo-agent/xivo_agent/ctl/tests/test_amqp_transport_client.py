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


import unittest
import pika

from mock import Mock, patch, ANY
from xivo_agent.ctl.amqp_transport_client import AMQPTransportClient


class TestAMQPTransportClient(unittest.TestCase):

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

    @patch('xivo_agent.ctl.amqp_transport_server.AMQPTransportServer')
    @patch('pika.ConnectionParameters')
    def test_create_and_connect(self, connection_params, constructor):
        AMQPTransportClient.create_and_connect('localhost')

        connection_params.assert_called_once_with(host='localhost')
        constructor.assert_called_once()

    def test_connect(self):
        self._new_transport()

        self.blocking_connection.assert_called_once()
        self.connection.channel.assert_called_once()

    def test_setup_queue(self):
        result = Mock()
        result.method = Mock()
        result.method.queue = Mock()
        self.channel.queue_declare.return_value = result

        self._new_transport()

        self.channel.queue_declare.assert_called_once_with(exclusive=True)
        self.channel.basic_consume.assert_called_once_with(ANY, no_ack=True, queue=result.method.queue)

    def test_rpc_call(self):
        transport = self._new_transport()
        with patch.object(transport, '_send_request') as send_request:
            with patch.object(transport, '_wait_for_response') as wait_for_response:
                transport.rpc_call('blah')
                send_request.assert_called_once()
                wait_for_response.assert_called_once()

    @patch('xivo_agent.ctl.amqp_transport_client.AMQPTransportClient._build_properties')
    def test_send_request(self, build_properties):
        transport = self._new_transport()
        transport._send_request(1, 'blah')

        self.channel.basic_publish.assert_called_once_with(
            exchange='',
            routing_key='xivo_agent',
            properties=ANY,
            body='blah'
        )

        build_properties.assert_called_once_with(1)

    def test_build_properties(self):
        transport = self._new_transport()
        transport._callback_queue = Mock()
        properties = transport._build_properties(1)

        self.assertTrue(isinstance(properties, pika.BasicProperties))

    def test_close(self):
        transport = self._new_transport()
        transport.close()
        self.connection.close.assert_called_once()

    def _new_transport(self):
        params = pika.ConnectionParameters(host='localhost')
        transport = AMQPTransportClient(params)

        return transport


if __name__ == "__main__":
    unittest.main()
