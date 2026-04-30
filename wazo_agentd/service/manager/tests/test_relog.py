# Copyright 2013-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock

from wazo_bus.resources.user_agent.event import UserAgentQueueLoggedInEvent

from wazo_agentd.service.action.login import LoginAction
from wazo_agentd.service.action.logoff import LogoffAction
from wazo_agentd.service.manager.relog import RelogManager


class TestRelogManager(unittest.TestCase):
    def setUp(self):
        self.login_action = Mock(LoginAction)
        self.logoff_action = Mock(LogoffAction)
        self.agent_status_dao = Mock()
        self.agent_dao = Mock()
        self.user_dao = Mock()
        self.bus_publisher = Mock()
        self.relog_manager = RelogManager(
            self.login_action,
            self.logoff_action,
            self.agent_dao,
            self.agent_status_dao,
            self.user_dao,
            self.bus_publisher,
        )

    def test_relog_all_agents(self):
        agent_id = 42
        agent = Mock()
        agent.id = agent_id
        agent_status = Mock()
        agent_status.agent_id = agent_id

        self.agent_dao.get_agent.return_value = agent
        self.agent_status_dao.get_logged_agent_ids.return_value = [agent_id]
        self.agent_status_dao.get_status.return_value = agent_status

        self.relog_manager.relog_all_agents()

        self.agent_status_dao.get_status.assert_called_once_with(agent_id)
        self.logoff_action.logoff_agent.assert_called_once_with(agent_status)
        self.agent_dao.get_agent.assert_called_once_with(agent_id)
        self.agent_status_dao.remove_agent_from_all_queues.assert_not_called()
        self.agent_status_dao.add_agent_to_queues.assert_not_called()
        self.login_action.login_agent.assert_called_once_with(
            agent, agent_status.extension, agent_status.context
        )
        self.bus_publisher.publish.assert_not_called()

    def test_relog_all_agents_all_queues_emits_event_for_newly_logged_queue(self):
        agent_id = 42
        tenant_uuid = 'tenant-uuid'
        queue_already_logged = Mock(id=10)
        queue_newly_logged = Mock(id=11)
        agent = Mock(
            id=agent_id,
            tenant_uuid=tenant_uuid,
            queues=[queue_already_logged, queue_newly_logged],
        )
        agent_status = Mock(agent_id=agent_id)
        user = Mock(uuid='user-uuid-1')

        self.agent_dao.get_agent.return_value = agent
        self.agent_dao.list_agent_enabled_queues.return_value = [queue_already_logged]
        self.agent_status_dao.get_logged_agent_ids.return_value = [agent_id]
        self.agent_status_dao.get_status.return_value = agent_status
        self.user_dao.find_all_by_agent_id.return_value = [user]

        self.relog_manager.relog_all_agents(all_queues=True)

        self.logoff_action.logoff_agent.assert_called_once_with(agent_status)
        self.agent_status_dao.remove_agent_from_all_queues.assert_called_once_with(
            agent_id
        )
        self.agent_status_dao.add_agent_to_queues.assert_called_once_with(
            agent_id, agent.queues
        )
        self.login_action.login_agent.assert_called_once_with(
            agent, agent_status.extension, agent_status.context
        )
        expected_event = UserAgentQueueLoggedInEvent(
            agent_id, queue_newly_logged.id, tenant_uuid, ['user-uuid-1']
        )
        self.bus_publisher.publish.assert_called_once_with(expected_event)

    def test_relog_all_agents_all_queues_no_event_when_nothing_changed(self):
        agent_id = 42
        queue = Mock(id=10)
        agent = Mock(id=agent_id, tenant_uuid='tenant-uuid', queues=[queue])
        agent_status = Mock(agent_id=agent_id)

        self.agent_dao.get_agent.return_value = agent
        self.agent_dao.list_agent_enabled_queues.return_value = [queue]
        self.agent_status_dao.get_logged_agent_ids.return_value = [agent_id]
        self.agent_status_dao.get_status.return_value = agent_status

        self.relog_manager.relog_all_agents(all_queues=True)

        self.bus_publisher.publish.assert_not_called()
