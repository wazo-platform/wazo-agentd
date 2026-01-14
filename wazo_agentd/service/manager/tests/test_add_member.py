# Copyright 2019-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock

from wazo_agentd.exception import AgentAlreadyInQueueError, QueueDifferentTenantError
from wazo_agentd.service.manager.add_member import AddMemberManager


class TestAddMemberManager(unittest.TestCase):
    def setUp(self):
        self.add_to_queue_action = Mock()
        self.amid_client = Mock()
        self.queue_member_dao = Mock()
        self.member_manager = AddMemberManager(
            self.add_to_queue_action,
            self.amid_client,
            self.queue_member_dao,
        )

    def test_add_agent_to_queue_same_tenant(self):
        agent = Mock(tenant_uuid='fake-tenant', queues=[])
        queue = Mock(tenant_uuid='fake-tenant')

        self.member_manager.add_agent_to_queue(agent, queue)

        self.add_to_queue_action.add_agent_to_queue.assert_called_once_with(
            agent, queue
        )
        self.queue_member_dao.add_agent_to_queue.assert_called_once_with(
            agent.id, agent.number, queue.name
        )
        self.amid_client.action.assert_called_once_with(
            'UserEvent',
            {
                'UserEvent': 'AgentAddedToQueue',
                'AgentID': agent.id,
                'AgentNumber': agent.number,
                'QueueName': queue.name,
            },
        )

    def test_add_agent_to_queue_different_tenant(self):
        agent = Mock(tenant_uuid='fake-tenant-1', queues=[])
        queue = Mock(tenant_uuid='fake-tenant-2')

        self.assertRaises(
            QueueDifferentTenantError,
            self.member_manager.add_agent_to_queue,
            agent,
            queue,
        )

        self.add_to_queue_action.add_agent_to_queue.assert_not_called()
        self.amid_client.action.assert_not_called()

    def test_add_agent_to_queue_already_in_queue(self):
        queue = Mock(tenant_uuid='fake-tenant', name='queue1')
        agent = Mock(tenant_uuid='fake-tenant', queues=[queue])

        self.assertRaises(
            AgentAlreadyInQueueError,
            self.member_manager.add_agent_to_queue,
            agent,
            queue,
        )

        self.add_to_queue_action.add_agent_to_queue.assert_not_called()
        self.amid_client.action.assert_not_called()
