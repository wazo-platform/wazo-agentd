# Copyright 2013-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from unittest.mock import Mock
from wazo_agentd.service.manager.pause import PauseManager
from wazo_agentd.service.manager.on_queue_agent_paused import OnQueueAgentPausedManager
from wazo_agentd.service.handler.pause import PauseHandler
from wazo_agentd.service.handler.on_queue import OnQueueHandler


class TestPauseHandler(unittest.TestCase):
    def setUp(self):
        self.pause_manager = Mock(PauseManager)
        self.on_queue_pause_manager = Mock(OnQueueAgentPausedManager)
        self.agent_status_dao = Mock()
        self.agent_dao = Mock()

        self.pause_handler = PauseHandler(self.pause_manager, self.agent_status_dao)
        self.on_queue_handler = OnQueueHandler(
            Mock(), Mock(), Mock(), self.on_queue_pause_manager, Mock(), self.agent_dao
        )
        self.tenants = ['fake-tenant']

    def test_pause_by_number(self):
        agent_number = '42'
        agent_status = Mock()
        reason = Mock()
        self.agent_status_dao.get_status_by_number.return_value = agent_status

        self.pause_handler.handle_pause_by_number(
            agent_number, reason, tenant_uuids=self.tenants
        )

        self.agent_status_dao.get_status_by_number.assert_called_once_with(
            agent_number, tenant_uuids=self.tenants
        )
        self.pause_manager.pause_agent.assert_called_once_with(agent_status, reason)

    def test_pause_queue_agent(self):
        self.on_queue_handler.handle_on_agent_paused(
            {
                'MemberName': 'aa/invalid-number-42',
                'PausedReason': 'a',
                'Queue': 'queue-1',
                'Interface': 'Local/id-2@agentcallback',
            }
        )
        self.on_queue_pause_manager.on_queue_agent_paused.assert_not_called()
        self.agent_dao.agent_with_number.assert_not_called()

        self.on_queue_handler.handle_on_agent_paused(
            {
                'MemberName': 'aa/42',
                'PausedReason': 'a',
                'Queue': 'queue-1',
                'Interface': 'Local/id-2@agentcallback',
            }
        )
        self.on_queue_pause_manager.on_queue_agent_paused.assert_called_once()

    def test_unpause_queue_agent(self):
        self.on_queue_handler.handle_on_agent_unpaused(
            {
                'MemberName': 'aa/invalid-number-42',
                'PausedReason': 'a',
                'Queue': 'queue-1',
                'Interface': 'Local/id-2@agentcallback',
            }
        )
        self.on_queue_pause_manager.on_queue_agent_unpaused.assert_not_called()
        self.agent_dao.agent_with_number.assert_not_called()

        self.on_queue_handler.handle_on_agent_unpaused(
            {
                'MemberName': 'aa/42',
                'PausedReason': 'a',
                'Queue': 'queue-1',
                'Interface': 'Local/id-2@agentcallback',
            }
        )
        self.on_queue_pause_manager.on_queue_agent_unpaused.assert_called_once()

    def test_unpause_by_number(self):
        agent_number = '42'
        agent_status = Mock()
        self.agent_status_dao.get_status_by_number.return_value = agent_status

        self.pause_handler.handle_unpause_by_number(
            agent_number, tenant_uuids=self.tenants
        )

        self.agent_status_dao.get_status_by_number.assert_called_once_with(
            agent_number, tenant_uuids=self.tenants
        )
        self.pause_manager.unpause_agent.assert_called_once_with(agent_status)
