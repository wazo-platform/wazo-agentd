# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
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

import json
import logging
import threading

from kombu import Queue
from kombu.mixins import ConsumerMixin
from xivo_bus.resources.agent.event import EditAgentEvent, DeleteAgentEvent
from xivo_bus.resources.queue.event import CreateQueueEvent, EditQueueEvent, DeleteQueueEvent

logger = logging.getLogger(__name__)


class AMQPInterface(object):

    def __init__(self, connection, exchange, server_proxy):
        self._thread = None
        self._worker = self._new_worker(connection, exchange, server_proxy)

    def _new_worker(self, connection, exchange, server_proxy):
        msg_handler = _MessageHandler([
            _EditAgentEventHandler(server_proxy),
            _DeleteAgentEventHandler(server_proxy),
            _CreateQueueEventHandler(server_proxy),
            _EditQueueEventHandler(server_proxy),
            _DeleteQueueEventHandler(server_proxy),
        ])
        return _Worker(connection, exchange, msg_handler)

    def start(self):
        self._thread = threading.Thread(target=self._run)
        self._thread.start()

    def _run(self):
        self._worker.run()

    def stop(self):
        if self._thread is None:
            return

        self._worker.should_stop = True
        self._thread.join()
        self._thread = None


class _Worker(ConsumerMixin):

    def __init__(self, connection, exchange, msg_handler):
        self.connection = connection
        self._exchange = exchange
        self._msg_handler = msg_handler

    def get_consumers(self, Consumer, channel):
        queues = [Queue(exchange=self._exchange, routing_key=routing_key, exclusive=True)
                  for routing_key in self._msg_handler.routing_keys()]
        return [Consumer(queues=queues, callbacks=[self._on_message])]

    def _on_message(self, body, message):
        message.ack()
        try:
            self._msg_handler.handle_msg(body)
        except Exception:
            logger.warning('Unexpected error while handling AMQP message', exc_info=True)


class _MessageHandler(object):

    def __init__(self, event_handlers):
        self._event_handlers = dict((event_handler.Event.name, event_handler)
                                    for event_handler in event_handlers)

    def routing_keys(self):
        return [event_handler.Event.routing_key for event_handler in self._event_handlers.itervalues()]

    def handle_msg(self, msg):
        decoded_msg = json.loads(msg)
        event_name = decoded_msg['name']
        self._event_handlers[event_name].handle_event(decoded_msg)


class _BaseEventHandler(object):

    def __init__(self, server_proxy):
        self._server_proxy = server_proxy


class _EditAgentEventHandler(_BaseEventHandler):

    Event = EditAgentEvent

    def handle_event(self, decoded_msg):
        self._server_proxy.on_agent_updated(decoded_msg['data']['id'])


class _DeleteAgentEventHandler(_BaseEventHandler):

    Event = DeleteAgentEvent

    def handle_event(self, decoded_msg):
        self._server_proxy.on_agent_deleted(decoded_msg['data']['id'])


class _CreateQueueEventHandler(_BaseEventHandler):

    Event = CreateQueueEvent

    def handle_event(self, decoded_msg):
        self._server_proxy.on_queue_added(decoded_msg['data']['id'])


class _EditQueueEventHandler(_BaseEventHandler):

    Event = EditQueueEvent

    def handle_event(self, decoded_msg):
        self._server_proxy.on_queue_updated(decoded_msg['data']['id'])


class _DeleteQueueEventHandler(_BaseEventHandler):

    Event = DeleteQueueEvent

    def handle_event(self, decoded_msg):
        self._server_proxy.on_queue_deleted(decoded_msg['data']['id'])
