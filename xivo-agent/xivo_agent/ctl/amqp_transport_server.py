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
import json

class AMQPTransportServer(object):

    _QUEUE_NAME = 'xivo_agent'

    def __init__(self, connection_params, request_callback):
        self._request_callback = request_callback
        self._connect(connection_params)
        self._setup_queue()

    def _connect(self, params):
        self._connection = pika.BlockingConnection(params)
        self._channel = self._connection.channel()

    def _setup_queue(self):
        self._channel.queue_declare(queue=self._QUEUE_NAME)
        self._channel.basic_qos(prefetch_count=1)
        self._channel.basic_consume(self._on_request, self._QUEUE_NAME)

    def _on_request(self, channel, method, properties, body):
        response = self._request_callback(body)

        response_properties = pika.BasicProperties(
            correlation_id=properties.correlation_id,
        )

        self._channel.basic_publish(
            exchange='',
            routing_key=properties.reply_to,
            properties=response_properties,
            body=response
        )

        self._channel.basic_ack(delivery_tag=method.delivery_tag)

    def run(self):
        self._channel.start_consuming()