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
from xivo_agent.exception import AgentServerError


class AMQPTransportServer(object):

    _QUEUE_NAME = 'xivo_agent'

    @classmethod
    def create_and_connect(cls, host, request_callback):
        connection_params = pika.ConnectionParameters(host=host)
        return cls(connection_params, request_callback)

    def __init__(self, connection_params, request_callback):
        self._request_callback = request_callback
        self._connect(connection_params)

    def _connect(self, params):
        self._connection = pika.BlockingConnection(params)
        self._channel = self._connection.channel()

    def run(self):
        self._setup_queue()
        self._channel.start_consuming()

    def _setup_queue(self):
        self._channel.queue_declare(queue=self._QUEUE_NAME)
        self._channel.basic_qos(prefetch_count=1)
        self._channel.basic_consume(self._on_request, self._QUEUE_NAME)

    def _on_request(self, channel, method, properties, body):
        try:
            response = self._request_callback(body)
        except AgentServerError as e:
            response = self._error_response(e)
            self._send_response(response, properties, method)
            raise

        self._send_response(response, properties, method)

    def _send_response(self, body, properties, method):

        response_properties = pika.BasicProperties(
            correlation_id=properties.correlation_id,
        )

        self._channel.basic_publish(
            exchange='',
            routing_key=properties.reply_to,
            properties=response_properties,
            body=body
        )

        self._channel.basic_ack(delivery_tag=method.delivery_tag)

    def close(self):
        self._channel.stop_consuming()
        self._connection.close()
        self._channel = None
        self._connection = None

    def _error_response(self, error):
        return str(error)
