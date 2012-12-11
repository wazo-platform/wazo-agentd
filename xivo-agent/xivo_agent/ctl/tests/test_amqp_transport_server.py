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

from mock import Mock, patch, ANY
from xivo_agent.ctl.amqp_transport_server import AMQPTransportServer

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

    @patch('xivo_agent.ctl.amqp_transport_server.AMQPTransportServer')
    @patch('pika.ConnectionParameters')
    def test_create_and_connect(self, connection_params, constructor):
        callback = Mock()
        transport = AMQPTransportServer.create_and_connect('localhost', callback)

        connection_params.assert_called_once_with(host='localhost')
        constructor.assert_called_once()

    def test_connect(self):
        transport = self._new_transport()

        self.connection.channel.assert_called_once_with()

    def test_setup_queue(self):
        transport = self._new_transport()

        self.channel.queue_declare.assert_called_once_with(queue='xivo_agent')
        self.channel.basic_qos.assert_called_once_with(prefetch_count=1)
        self.channel.basic_consume.assert_called_once_with(ANY, 'xivo_agent')

    def test_on_request(self):
        response = "{'response': 'success'}"

        request_callback = Mock()
        request_callback.return_value = response

        properties = Mock()
        properties.correlation_id = 1
        properties.reply_to = 'consumer1'

        method = Mock()
        method.delivery_tag = 'delivery_tag'

        body = '{"cmd": {"a": 1}, "name": "foobar"}'

        transport = self._new_transport(request_callback)
        transport._on_request(None, method, properties, body)

        self.channel.basic_publish.assert_called_once_with(
            exchange='',
            routing_key=properties.reply_to,
            properties=ANY,
            body=response)

        self.channel.basic_ack.assert_called_once()

    def test_run(self):
        transport = self._new_transport()
        transport.run()
        self.channel.start_consuming.assert_called_once()

    def test_close(self):
        transport = self._new_transport()
        transport.close()

        self.channel.stop_consuming.assert_called_once()
        self.connection.close.assert_called_once()


    def _new_transport(self, request_callback=None):
        request_callback = request_callback or Mock()
        host = 'localhost'
        params = pika.ConnectionParameters(host=host)

        transport = AMQPTransportServer(params, request_callback)

        return transport

if __name__ == "__main__":
    unittest.main()