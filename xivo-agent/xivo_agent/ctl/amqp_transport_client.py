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
import uuid
from xivo_agent.ctl.response import CommandResponse

class AMQPTransportClient(object):

    _QUEUE_NAME = 'xivo_agent'

    def __init__(self):
        self._connect()
        self._setup_queue()
        self._correlation_id = None
        self._response = None

    def _connect(self, host):
        params = pika.ConnectionParameters(host=host)
        self._connection = pika.BlockingConnection(params)
        self._channel = self.connection.channel()

    def _setup_queue(self):
        result = self._channel.queue_declare(exclusive=True)
        self._callback_queue = result.method.queue

        self.channel.basic_consume(
            self._on_response,
            no_ack=True,
            queue=self.callback_queue
        )

    def _on_response(self, channel, method, properties, body):
        if self._correlation_id == properties.correlation_id:
            response = self._unmarshal_response(body)
            self._process_response(response)

    def send_command(self, command):
        if self._response:
            raise Exception("already waiting after command %r" % command)

        self._response = None
        self._correlation_id = str(uuid.uuid4())

        body = self._marshal_command(command)

        properties = pika.BasicProperties(
            reply_to=self._callback_queue,
            correlation_id=self._correlation_id
        )

        self._channel.basic_publish(
            exchange='',
            routing_key=self._QUEUE_NAME,
            properties=properties,
            body=body
        )

        while self._response is None:
            self._connection.process_data_events()

        response = self._unmarshal_response(self._response)
        self._response = None
        return response

    def _marshal_command(self, command):
        return json.dumps({'name': command.name, 'cmd': command.marshal()})

    def _unmarshal_response(self, data):
        msg = json.loads(data)
        return CommandResponse.unmarshal(msg)



