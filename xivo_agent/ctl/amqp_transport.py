# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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
import uuid
import threading

from xivo_agent.ctl.config import BusConfig


class _AMQPTransport(object):

    def __init__(self):
        self._lock = threading.Lock()

    def exchange_declare(self, name, type_, durable):
        with self._lock:
            self._channel.exchange_declare(exchange=name, type=type_, durable=durable)

    def _connect(self, params):
        self._connection = pika.BlockingConnection(params)
        self._channel = self._connection.channel()

    def send(self, exchange, routing_key, body):
        with self._lock:
            self._send_request(exchange, routing_key, body, None)

    def _send_request(self, exchange, routing_key, body, properties):
        if self._connection.is_closed:
            raise IOError('Bus connection is closed')
        self._channel.basic_publish(
            exchange=exchange,
            routing_key=routing_key,
            properties=properties,
            body=body
        )

    def close(self):
        with self._lock:
            self._connection.close()
            self._channel = None
            self._connection = None


class AMQPTransportServer(_AMQPTransport):

    @classmethod
    def create_and_connect(cls, request_callback, queue_name=None, config=None):
        if not config:
            config = BusConfig()
        connection_params = config.to_connection_params()
        return cls(connection_params, request_callback, queue_name)

    def __init__(self, connection_params, request_callback, queue_name):
        super(AMQPTransportServer, self).__init__()
        self._queue_name = queue_name
        self._request_callback = request_callback
        self._connect(connection_params)

    def run(self):
        self._setup_queue()
        self._channel.start_consuming()

    def _setup_queue(self):
        if self._queue_name is None:
            result = self._channel.queue_declare()
            queue_name = result.method.queue
        else:
            queue_name = self._queue_name
            self._channel.queue_declare(queue=self._queue_name)

        self._channel.basic_qos(prefetch_count=1)
        self._channel.basic_consume(self._on_request, queue_name)

    def _on_request(self, channel, method, properties, body):
        try:
            response = self._request_callback(body)
        except Exception as e:
            response = self._error_response(e)

        if properties.reply_to:
            self._send_response(response, properties)
        self._acknowledge_request(method)

    def _send_response(self, body, properties):
        response_properties = pika.BasicProperties(
            correlation_id=properties.correlation_id,
        )

        self._channel.basic_publish(
            exchange='',
            routing_key=properties.reply_to,
            properties=response_properties,
            body=body
        )

    def _acknowledge_request(self, method):
        self._channel.basic_ack(delivery_tag=method.delivery_tag)

    def close(self):
        self._channel.stop_consuming()
        super(AMQPTransportServer, self).close()

    def _error_response(self, error):
        return str(error)


class AMQPTransportClient(_AMQPTransport):

    @classmethod
    def create_and_connect(cls, config=None):
        if not config:
            config = BusConfig()
        connection_params = config.to_connection_params()
        return cls(connection_params)

    def __init__(self, connection_params):
        super(AMQPTransportClient, self).__init__()
        self._connect(connection_params)
        self._setup_queue()
        self._correlation_id = None
        self._response = None

    def _setup_queue(self):
        result = self._channel.queue_declare(exclusive=True)
        self._callback_queue = result.method.queue

        self._channel.basic_consume(
            self._on_response,
            no_ack=True,
            queue=self._callback_queue
        )

    def _on_response(self, channel, method, properties, body):
        if self._correlation_id == properties.correlation_id:
            self._response = body

    def rpc_call(self, exchange, routing_key, request):
        with self._lock:
            self._response = None
            self._correlation_id = str(uuid.uuid4())
            properties = self._build_rpc_call_properties()

            self._send_request(exchange, routing_key, request, properties)
            return self._wait_for_response()

    def _build_rpc_call_properties(self):
        properties = pika.BasicProperties(
            reply_to=self._callback_queue,
            correlation_id=self._correlation_id
        )

        return properties

    def _wait_for_response(self):
        while self._response is None:
            self._connection.process_data_events()

        return self._response
