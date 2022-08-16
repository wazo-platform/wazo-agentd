# Copyright 2017-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from unittest.mock import Mock, sentinel as s
from hamcrest import assert_that, has_entries

from ..on_queue_agent_paused import OnQueueAgentPausedManager
from ..on_queue_agent_paused import AgentPausedEvent, AgentUnpausedEvent


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
        tenant_uuid = '00000000-0000-4000-8000-0000000055ff'
        self.agent_dao.agent_with_id.return_value = Mock(tenant_uuid=tenant_uuid)
        self.user_dao.find_all_by_agent_id.return_value = [
            Mock(uuid='42'),
            Mock(uuid='43'),
        ]
        self.manager.on_queue_agent_paused(10, s.number, s.reason, s.queue)

        expected_event = AgentPausedEvent(
            10, s.number, s.queue, s.reason, tenant_uuid, ['42', '43']
        )
        assert_that(
            expected_event.headers,
            has_entries(
                {
                    'user_uuid:42': True,
                    'user_uuid:43': True,
                    'tenant_uuid': tenant_uuid,
                }
            ),
        )

        self.agent_status_dao.update_pause_status.assert_called_once_with(
            10, True, s.reason
        )
        self.bus_publisher.publish.assert_called_once_with(expected_event)

    def test_on_queue_agent_unpaused(self):
        tenant_uuid = '00000000-0000-4000-8000-000000c0fefe'
        self.agent_dao.agent_with_id.return_value = Mock(tenant_uuid=tenant_uuid)
        self.user_dao.find_all_by_agent_id.return_value = [
            Mock(uuid='42'),
            Mock(uuid='43'),
        ]

        self.manager.on_queue_agent_unpaused(10, s.number, s.reason, s.queue)

        expected_event = AgentUnpausedEvent(
            10, s.number, s.queue, s.reason, tenant_uuid, ['42', '43']
        )
        assert_that(
            expected_event.headers,
            has_entries(
                {
                    'user_uuid:42': True,
                    'user_uuid:43': True,
                    'tenant_uuid': tenant_uuid,
                }
            ),
        )

        self.agent_status_dao.update_pause_status.assert_called_once_with(
            10, False, s.reason
        )
        self.bus_publisher.publish.assert_called_once_with(expected_event)
