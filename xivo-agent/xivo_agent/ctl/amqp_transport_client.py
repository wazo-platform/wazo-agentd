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


import pika
import uuid


class AMQPTransportClient(object):

    _QUEUE_NAME = 'xivo_agent'

    @classmethod
    def create_and_connect(cls, host, port):
        connection_params = pika.ConnectionParameters(host=host, port=port)
        return cls(connection_params)

    def __init__(self, connection_params):
        self._connect(connection_params)
        self._setup_queue()
        self._correlation_id = None
        self._response = None

    def _connect(self, params):
        self._connection = pika.BlockingConnection(params)
        self._channel = self._connection.channel()

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

    def rpc_call(self, request):
        self._response = None
        self._correlation_id = str(uuid.uuid4())

        self._send_request(request)
        return self._wait_for_response()

    def _send_request(self, request):
        properties = self._build_properties()

        self._channel.basic_publish(
            exchange='',
            routing_key=self._QUEUE_NAME,
            properties=properties,
            body=request
        )

    def _build_properties(self):
        properties = pika.BasicProperties(
            reply_to=self._callback_queue,
            correlation_id=self._correlation_id
        )

        return properties

    def _wait_for_response(self):
        while self._response is None:
            self._connection.process_data_events()

        return self._response

    def close(self):
        self._connection.close()
        self._channel = None
        self._connection = None
