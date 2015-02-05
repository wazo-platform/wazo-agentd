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

from xivo_agent.ctl.amqp_transport import AMQPTransportClient
from xivo_agent.ctl.producer import BusProducer
from xivo_agent.ctl.config import BusConfig


class TestBusProducer(unittest.TestCase):

    def setUp(self):
        self.marshaler = Mock()
        self.transport = Mock(AMQPTransportClient)
        self.config = Mock(BusConfig)
        self.bus_producer = BusProducer()
        self.bus_producer._marshaler = self.marshaler
        self.bus_producer._transport = self.transport

    @patch('xivo_agent.ctl.producer.AMQPTransportClient')
    def test_connect_no_transport(self, amqp_client_constructor):
        client = BusProducer(self.config)
        client.connect()

        amqp_client_constructor.create_and_connect.assert_called_once_with(config=self.config)

    @patch('xivo_agent.ctl.producer.AMQPTransportClient', Mock())
    def test_connect_already_connected(self):
        client = BusProducer()
        client.connect()

        self.assertRaises(Exception, client.connect)

    @patch('xivo_agent.ctl.producer.AMQPTransportClient')
    def test_close_transport_with_no_connection(self, amqp_client):
        client = BusProducer()
        client.close()
        self.assertFalse(amqp_client.create_and_connect.called)

    @patch('xivo_agent.ctl.producer.AMQPTransportClient')
    def test_connect_and_close_opens_and_closes_transport(self, amqp_client):
        transport = Mock()
        amqp_client.create_and_connect.return_value = transport

        client = BusProducer(self.config)
        client.connect()
        client.close()

        amqp_client.create_and_connect.assert_called_once_with(config=self.config)
        transport.close.assert_called_once_with()

    def test_declare_exchange(self):
        name = 'xivo-ami'
        exchange_type = 'topic'
        durable = True

        self.bus_producer.declare_exchange(name, exchange_type, durable)

        self.transport.exchange_declare.assert_called_once_with(name, exchange_type, durable)

    def test_publish_event(self):
        event = Mock()
        event.name = 'foobar'
        exchange = 'xivo-ami'
        routing_key = event.name
        request = Mock()
        self.marshaler.marshal_message.return_value = request

        self.bus_producer.publish_event(exchange, routing_key, event)

        self.marshaler.marshal_message.assert_called_once_with(event)
        self.transport.send.assert_called_once_with(exchange, routing_key, request)
