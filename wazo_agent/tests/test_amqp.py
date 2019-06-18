# Copyright (C) 2015-2016 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import unittest

from mock import Mock, sentinel
from wazo_agent.amqp import AMQPInterface, _EditAgentEventHandler, \
    _DeleteAgentEventHandler, _CreateQueueEventHandler, _EditQueueEventHandler, \
    _DeleteQueueEventHandler, _MessageHandler, _Worker
from wazo_agent.service.proxy import ServiceProxy


class TestAMQPInterface(unittest.TestCase):

    def setUp(self):
        self.connection = Mock()
        self.exchange = Mock()
        self.service_proxy = Mock()
        self.amqp_interface = AMQPInterface(self.connection, self.exchange, self.service_proxy)

    def test_start_and_stop(self):
        worker = Mock()
        self.amqp_interface._worker = worker

        self.amqp_interface.start()
        self.amqp_interface.stop()

        worker.run.assert_called_once_with()
        self.assertTrue(worker.should_stop)


class TestWorker(unittest.TestCase):

    def setUp(self):
        self.connection = Mock()
        self.exchange = Mock()
        self.msg_handler = Mock(_MessageHandler)
        self.worker = _Worker(self.connection, self.exchange, self.msg_handler)

    def test_on_message(self):
        message = Mock()

        self.worker._on_message(sentinel.body, message)

        message.ack.assert_called_once_with()
        self.msg_handler.handle_msg.assert_called_once_with(sentinel.body)


class TestMessageHandler(unittest.TestCase):

    def setUp(self):
        self.event_handler = Mock()
        self.event_handler.Event.name = 'foobar'
        self.msg_handler = _MessageHandler([self.event_handler])

    def test_routing_keys(self):
        routing_keys = self.msg_handler.routing_keys()

        self.assertEqual(routing_keys, [self.event_handler.Event.routing_key])

    def test_handle_msg(self):
        msg = {'name': self.event_handler.Event.name}

        self.msg_handler.handle_msg(msg)

        self.event_handler.handle_event.assert_called_once_with(msg)

    def test_handle_msg_invalid(self):
        decoded_msg = {'name': 'sicilian pastorale'}
        msg = json.dumps(decoded_msg)

        self.assertRaises(Exception, self.msg_handler.handle_msg, msg)
        self.assertFalse(self.event_handler.handle_event.called)


class TestEventHandler(unittest.TestCase):

    def setUp(self):
        self.service_proxy = Mock(ServiceProxy)
        self.item_id = 42
        self.decoded_msg = {'data': {'id': self.item_id}}

    def test_edit_agent(self):
        handler = _EditAgentEventHandler(self.service_proxy)

        handler.handle_event(self.decoded_msg)

        self.service_proxy.on_agent_updated.assert_called_once_with(self.item_id)

    def test_delete_agent(self):
        handler = _DeleteAgentEventHandler(self.service_proxy)

        handler.handle_event(self.decoded_msg)

        self.service_proxy.on_agent_deleted.assert_called_once_with(self.item_id)

    def test_create_queue(self):
        handler = _CreateQueueEventHandler(self.service_proxy)

        handler.handle_event(self.decoded_msg)

        self.service_proxy.on_queue_added.assert_called_once_with(self.item_id)

    def test_edit_queue(self):
        handler = _EditQueueEventHandler(self.service_proxy)

        handler.handle_event(self.decoded_msg)

        self.service_proxy.on_queue_updated.assert_called_once_with(self.item_id)

    def test_delete_queue(self):
        handler = _DeleteQueueEventHandler(self.service_proxy)

        handler.handle_event(self.decoded_msg)

        self.service_proxy.on_queue_deleted.assert_called_once_with(self.item_id)
