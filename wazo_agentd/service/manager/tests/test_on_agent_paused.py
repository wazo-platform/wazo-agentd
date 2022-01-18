# Copyright 2017-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from mock import Mock, sentinel as s

from ..on_queue_agent_paused import OnQueueAgentPausedManager
from ..on_queue_agent_paused import PauseAgentEvent, UnpauseAgentEvent


class TestOnQueueAgentPausedManager(unittest.TestCase):
    def setUp(self):
        self.agent_status_dao = Mock()
        self.user_dao = Mock()
        self.agent_dao = Mock()
        self.bus_publisher = Mock()

        self.manager = OnQueueAgentPausedManager(
            self.agent_status_dao, self.user_dao, self.agent_dao, self.bus_publisher
        )

    def test_on_queue_agent_paused(self):
        tenant_uuid = '00000000-0000-0000-0000-0000000055ff'
        self.agent_dao.agent_with_id.return_value = Mock(tenant_uuid=tenant_uuid)
        self.user_dao.find_all_by_agent_id.return_value = [
            Mock(uuid='42'),
            Mock(uuid='43'),
        ]
        self.manager.on_queue_agent_paused(10, s.number, s.reason, s.queue)

        expected_event = PauseAgentEvent(10, s.number, s.queue, s.reason)
        expected_headers = {
            'user_uuid:42': True,
            'user_uuid:43': True,
            'agent_id:10': True,
            'tenant_uuid': tenant_uuid,
        }

        self.agent_status_dao.update_pause_status.assert_called_once_with(
            10, True, s.reason
        )
        self.bus_publisher.publish_soon.assert_called_once_with(
            expected_event, headers=expected_headers
        )

    def test_on_queue_agent_unpaused(self):
        tenant_uuid = '00000000-0000-0000-0000-000000c0fefe'
        self.agent_dao.agent_with_id.return_value = Mock(tenant_uuid=tenant_uuid)
        self.user_dao.find_all_by_agent_id.return_value = [
            Mock(uuid='42'),
            Mock(uuid='43'),
        ]

        self.manager.on_queue_agent_unpaused(10, s.number, s.reason, s.queue)

        expected_event = UnpauseAgentEvent(10, s.number, s.queue, s.reason)
        expected_event.routing_key = 'status.agent.unpause'
        expected_headers = {
            'user_uuid:42': True,
            'user_uuid:43': True,
            'agent_id:10': True,
            'tenant_uuid': tenant_uuid,
        }

        self.agent_status_dao.update_pause_status.assert_called_once_with(
            10, False, s.reason
        )
        self.bus_publisher.publish_soon.assert_called_once_with(
            expected_event, headers=expected_headers
        )
