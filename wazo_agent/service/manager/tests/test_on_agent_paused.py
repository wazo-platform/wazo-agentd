# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

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
        self.user_dao = Mock()
        self.bus_publisher = Mock()

        self.manager = OnQueueAgentPausedManager(self.agent_status_dao, self.user_dao, self.bus_publisher)

    def test_on_queue_agent_paused(self):
        self.user_dao.find_all_by_agent_id.return_value = [Mock(uuid='42'), Mock(uuid='43')]

        self.manager.on_queue_agent_paused(10, s.number, s.reason, s.queue)

        expected_event = ArbitraryEventMatcher(
            name='agent_paused',
            body={'agent_id': 10,
                  'agent_number': s.number,
                  'queue': s.queue,
                  'paused': True,
                  'paused_reason': s.reason},
            required_acl='events.statuses.agents',
        )
        expected_event.routing_key = 'status.agent.pause'
        expected_headers = {'user_uuid:42': True, 'user_uuid:43': True, 'agent_id:10': True}

        self.agent_status_dao.update_pause_status.assert_called_once_with(10, True, s.reason)
        self.bus_publisher.publish.assert_called_once_with(expected_event, headers=expected_headers)

    def test_on_queue_agent_unpaused(self):
        self.user_dao.find_all_by_agent_id.return_value = [Mock(uuid='42'), Mock(uuid='43')]

        self.manager.on_queue_agent_unpaused(10, s.number, s.reason, s.queue)

        expected_event = ArbitraryEventMatcher(
            name='agent_unpaused',
            body={'agent_id': 10,
                  'agent_number': s.number,
                  'queue': s.queue,
                  'paused': False,
                  'paused_reason': s.reason},
            required_acl='events.statuses.agents',
        )
        expected_event.routing_key = 'status.agent.unpause'
        expected_headers = {'user_uuid:42': True, 'user_uuid:43': True, 'agent_id:10': True}

        self.agent_status_dao.update_pause_status.assert_called_once_with(10, False, s.reason)
        self.bus_publisher.publish.assert_called_once_with(expected_event, headers=expected_headers)
