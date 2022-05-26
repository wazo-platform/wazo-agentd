# Copyright 2013-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock
from wazo_agentd.service.handler.logoff import LogoffHandler
from wazo_agentd.service.manager.logoff import LogoffManager


class TestLogoffHandler(unittest.TestCase):
    def setUp(self):
        self.logoff_manager = Mock(LogoffManager)
        self.agent_status_dao = Mock()
        self.logoff_handler = LogoffHandler(self.logoff_manager, self.agent_status_dao)
        self.tenants = ['fake-tenant']

    def test_handle_logoff_by_id(self):
        agent_id = 10
        agent_status = Mock()
        self.agent_status_dao.get_status.return_value = agent_status

        self.logoff_handler.handle_logoff_by_id(agent_id, tenant_uuids=self.tenants)

        self.agent_status_dao.get_status.assert_called_once_with(
            agent_id, tenant_uuids=self.tenants
        )
        self.logoff_manager.logoff_agent.assert_called_once_with(agent_status)

    def test_handle_logoff_by_number(self):
        agent_number = '10'
        agent_status = Mock()
        self.agent_status_dao.get_status_by_number.return_value = agent_status

        self.logoff_handler.handle_logoff_by_number(
            agent_number, tenant_uuids=self.tenants
        )

        self.agent_status_dao.get_status_by_number.assert_called_once_with(
            agent_number, tenant_uuids=self.tenants
        )
        self.logoff_manager.logoff_agent.assert_called_once_with(agent_status)

    def test_handle_logoff_user_agent(self):
        user_uuid = 'my-user-uuid'
        agent_status = Mock()
        self.agent_status_dao.get_status_by_user.return_value = agent_status

        self.logoff_handler.handle_logoff_user_agent(
            user_uuid, tenant_uuids=self.tenants
        )

        self.agent_status_dao.get_status_by_user.assert_called_once_with(
            user_uuid, tenant_uuids=self.tenants
        )
        self.logoff_manager.logoff_user_agent.assert_called_once_with(
            user_uuid, agent_status, tenant_uuids=self.tenants
        )
