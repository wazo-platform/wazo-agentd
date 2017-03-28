# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import Mock, sentinel as s

from ..on_queue_agent_call_changed import OnQueueAgentCallChangedManager, ArbitraryEvent


class ArbitraryEventMatcher(ArbitraryEvent):

    def __eq__(self, other):
        return (self.name == other.name
                and self._body == other._body
                and self.required_acl == other.required_acl
                and self.routing_key == other.routing_key)

    def __ne__(self, other):
        return not self == other


class TestOnQueueAgentCallChangedManager(unittest.TestCase):

    def setUp(self):
        self.agent_status_dao = Mock()
        self.bus_publisher = Mock()

        self.manager = OnQueueAgentCallChangedManager(self.agent_status_dao, self.bus_publisher)

    def test_on_queue_agent_call_changed_on_call_true(self):
        self.manager.on_queue_call_status_changed(s.id_, s.number, s.queue, True)

        expected_event = ArbitraryEventMatcher(
            name='agent_call_changed',
            body={'agent_id': s.id_,
                  'agent_number': s.number,
                  'queue': s.queue,
                  'on_call': True},
            required_acl='events.statuses.agents',
        )
        expected_event.routing_key = 'status.agent.call'

        self.agent_status_dao.update_on_call_status.assert_called_once_with(s.id_, True)
        self.bus_publisher.publish.assert_called_once_with(expected_event)

    def test_on_queue_agent_call_changed_on_call_false(self):
        self.manager.on_queue_call_status_changed(s.id_, s.number, s.queue, False)

        expected_event = ArbitraryEventMatcher(
            name='agent_call_changed',
            body={'agent_id': s.id_,
                  'agent_number': s.number,
                  'queue': s.queue,
                  'on_call': False},
            required_acl='events.statuses.agents',
        )
        expected_event.routing_key = 'status.agent.call'

        self.agent_status_dao.update_on_call_status.assert_called_once_with(s.id_, False)
        self.bus_publisher.publish.assert_called_once_with(expected_event)
