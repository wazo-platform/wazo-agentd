# Copyright 2015-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from contextlib import contextmanager
from threading import Thread

import kombu

from kombu.mixins import ConsumerMixin
from xivo_bus import (
    Marshaler,
    Publisher as _Publisher,
)
from xivo_bus.resources.agent.event import EditAgentEvent, DeleteAgentEvent
from xivo_bus.resources.queue.event import CreateQueueEvent, EditQueueEvent, DeleteQueueEvent
from xivo_bus.resources.ami.event import AMIEvent

logger = logging.getLogger(__name__)


@contextmanager
def consumer_thread(consumer):
    thread_name = 'bus_consumer_thread'
    thread = Thread(target=consumer.run, name=thread_name)
    thread.start()
    try:
        yield
    finally:
        logger.debug('stopping bus consumer thread')
        consumer.stop()
        logger.debug('joining bus consumer thread')
        thread.join()


# TODO use same mechanic as other services  when we will have integration tests
class Consumer(ConsumerMixin):

    def __init__(self, global_config):
        self._bus_url = 'amqp://{username}:{password}@{host}:{port}//'.format(**global_config['bus'])
        self._exchange = kombu.Exchange(
            global_config['bus']['exchange_name'],
            type=global_config['bus']['exchange_type'],
        )
        self._queue = kombu.Queue(exclusive=True)
        self._is_running = False
        self._msg_handler = None

    def register_service(self, service_proxy):
        self._msg_handler = _MessageHandler([
            _EditAgentEventHandler(service_proxy),
            _DeleteAgentEventHandler(service_proxy),
            _CreateQueueEventHandler(service_proxy),
            _EditQueueEventHandler(service_proxy),
            _DeleteQueueEventHandler(service_proxy),
            _PauseAgentEventHandler(service_proxy),
        ])

    def run(self):
        logger.info("Running AMQP consumer")
        with kombu.Connection(self._bus_url) as connection:
            self.connection = connection
            super().run()

    def get_consumers(self, Consumer, channel):
        queues = [kombu.Queue(exchange=self._exchange, routing_key=routing_key, exclusive=True)
                  for routing_key in self._msg_handler.routing_keys()]
        return [Consumer(queues=queues, callbacks=[self._on_message])]

    def _on_message(self, body, message):
        message.ack()
        try:
            self._msg_handler.handle_msg(body)
        except Exception:
            logger.warning('Unexpected error while handling AMQP message', exc_info=True)

    def stop(self):
        self.should_stop = True


class Publisher:

    def __init__(self, config):
        self._config = config['bus']
        self._uuid = config['uuid']
        self._url = 'amqp://{username}:{password}@{host}:{port}//'.format(**self._config)

    def publish(self, event, headers=None):
        bus_connection = kombu.Connection(self._url)
        bus_exchange = kombu.Exchange(
            self._config['exchange_name'],
            type=self._config['exchange_type'],
        )
        bus_producer = kombu.Producer(bus_connection, exchange=bus_exchange, auto_declare=True)
        bus_marshaler = Marshaler(self._uuid)
        _Publisher(bus_producer, bus_marshaler).publish(event, headers=headers)


class _MessageHandler:

    def __init__(self, event_handlers):
        self._event_handlers = dict((event_handler.Event.name, event_handler)
                                    for event_handler in event_handlers)

    def routing_keys(self):
        return [event_handler.Event.routing_key for event_handler in self._event_handlers.values()]

    def handle_msg(self, decoded_msg):
        event_name = decoded_msg['name']
        self._event_handlers[event_name].handle_event(decoded_msg)


class _BaseEventHandler:

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
