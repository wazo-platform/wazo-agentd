# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import logging
import threading

from kombu import Queue
from kombu.mixins import ConsumerMixin
from xivo_bus.resources.agent.event import EditAgentEvent, DeleteAgentEvent
from xivo_bus.resources.queue.event import CreateQueueEvent, EditQueueEvent, DeleteQueueEvent
from xivo_bus.resources.ami.event import AMIEvent

logger = logging.getLogger(__name__)


class AMQPInterface(object):

    def __init__(self, connection, exchange, service_proxy):
        self._thread = None
        self._worker = self._new_worker(connection, exchange, service_proxy)

    def _new_worker(self, connection, exchange, service_proxy):
        msg_handler = _MessageHandler([
            _EditAgentEventHandler(service_proxy),
            _DeleteAgentEventHandler(service_proxy),
            _CreateQueueEventHandler(service_proxy),
            _EditQueueEventHandler(service_proxy),
            _DeleteQueueEventHandler(service_proxy),
            _PauseAgentEventHandler(service_proxy),
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

    def handle_msg(self, decoded_msg):
        event_name = decoded_msg['name']
        self._event_handlers[event_name].handle_event(decoded_msg)


class _BaseEventHandler(object):

    def __init__(self, service_proxy):
        self._service_proxy = service_proxy


class _EditAgentEventHandler(_BaseEventHandler):

    Event = EditAgentEvent

    def handle_event(self, decoded_msg):
        self._service_proxy.on_agent_updated(decoded_msg['data']['id'])


class _DeleteAgentEventHandler(_BaseEventHandler):

    Event = DeleteAgentEvent

    def handle_event(self, decoded_msg):
        self._service_proxy.on_agent_deleted(decoded_msg['data']['id'])


class _CreateQueueEventHandler(_BaseEventHandler):

    Event = CreateQueueEvent

    def handle_event(self, decoded_msg):
        self._service_proxy.on_queue_added(decoded_msg['data']['id'])


class _EditQueueEventHandler(_BaseEventHandler):

    Event = EditQueueEvent

    def handle_event(self, decoded_msg):
        self._service_proxy.on_queue_updated(decoded_msg['data']['id'])


class _DeleteQueueEventHandler(_BaseEventHandler):

    Event = DeleteQueueEvent

    def handle_event(self, decoded_msg):
        self._service_proxy.on_queue_deleted(decoded_msg['data']['id'])


class AgentPauseEvent(AMIEvent):
    name = 'QueueMemberPause'
    routing_key = 'ami.{}'.format(name)


class _PauseAgentEventHandler(_BaseEventHandler):

    Event = AgentPauseEvent

    def handle_event(self, decoded_msg):
        if decoded_msg['data']['Paused'] == '1':
            self._service_proxy.on_agent_paused(decoded_msg['data'])
        else:
            self._service_proxy.on_agent_unpaused(decoded_msg['data'])
