# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import Mock, sentinel as s

from ..on_queue_agent_paused import OnQueueAgentPausedManager, ArbitraryEvent


class ArbitraryEventMatcher(ArbitraryEvent):

    def __eq__(self, other):
        return (self.name == other.name
                and self._body == other._body
                and self.required_acl == other.required_acl
                and self.routing_key == other.routing_key)

    def __ne__(self, other):
        return not self == other


class TestOnQueueAgentPausedManager(unittest.TestCase):

    def setUp(self):
        self.agent_status_dao = Mock()
        self.bus_publisher = Mock()

        self.manager = OnQueueAgentPausedManager(self.agent_status_dao, self.bus_publisher)

    def test_on_queue_agent_paused(self):
        self.manager.on_queue_agent_paused(s.id_, s.number, s.reason, s.queue)

        expected_event = ArbitraryEventMatcher(
            name='agent_paused',
            body={'agent_id': s.id_,
                  'agent_number': s.number,
                  'queue': s.queue,
                  'paused': True,
                  'pausedReason': s.reason},
            required_acl='events.statuses.agents',
        )
        expected_event.routing_key = 'status.agent.pause'

        self.agent_status_dao.update_pause_status.assert_called_once_with(s.id_, True, s.reason)
        self.bus_publisher.publish.assert_called_once_with(expected_event)

    def test_on_queue_agent_unpaused(self):
        self.manager.on_queue_agent_unpaused(s.id_, s.number, s.reason, s.queue)

        expected_event = ArbitraryEventMatcher(
            name='agent_unpaused',
            body={'agent_id': s.id_,
                  'agent_number': s.number,
                  'queue': s.queue,
                  'paused': False,
                  'pausedReason': s.reason},
            required_acl='events.statuses.agents',
        )
        expected_event.routing_key = 'status.agent.unpause'

        self.agent_status_dao.update_pause_status.assert_called_once_with(s.id_, False, s.reason)
        self.bus_publisher.publish.assert_called_once_with(expected_event)
