# Copyright 2013-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock

from wazo_agentd.exception import ContextDifferentTenantError, NoSuchExtensionError
from wazo_agentd.service.manager.login import LoginManager


class TestLoginManager(unittest.TestCase):
    def setUp(self):
        self.login_action = Mock()
        self.agent_status_dao = Mock()
        self.context_dao = Mock()
        self.line_dao = Mock()
        self.login_manager = LoginManager(
            self.login_action,
            self.agent_status_dao,
            self.context_dao,
            self.line_dao,
        )

    def test_login_agent(self):
        agent = Mock(tenant_uuid='fake-tenant')
        extension = '1001'
        context = 'default'
        context_mock = Mock(name=context, tenant_uuid='fake-tenant')
        self.context_dao.get.return_value = context_mock

        self.agent_status_dao.get_status.return_value = None
        self.agent_status_dao.is_extension_in_use.return_value = False

        self.login_manager.login_agent(agent, extension, context)

        self.login_action.login_agent.assert_called_once_with(
            agent, extension, context, None
        )

    def test_login_agent_multi_tenant(self):
        agent = Mock(tenant_uuid='fake-tenant-1')
        extension = '1001'
        context = 'default'
        context_mock = Mock(name=context, tenant_uuid='fake-tenant-2')
        self.context_dao.get.return_value = context_mock

        self.agent_status_dao.get_status.return_value = None
        self.agent_status_dao.is_extension_in_use.return_value = False

        self.assertRaises(
            ContextDifferentTenantError,
            self.login_manager.login_agent,
            agent,
            extension,
            context,
        )

        self.login_action.login_agent.assert_not_called()

    def test_login_user_agent(self):
        agent = Mock(tenant_uuid='fake-tenant')
        user_uuid = 'my-user-uuid'
        line_id = 12

        self.agent_status_dao.get_status.return_value = None
        self.line_dao.is_line_owned_by_user.return_value = True

        self.login_manager.login_user_agent(agent, user_uuid, line_id)

        self.login_action.login_agent_on_line.assert_called_once_with(agent, line_id)

    def test_login_agent_with_endpoint(self):
        agent = Mock(tenant_uuid='fake-tenant')
        extension = '1001'
        context = 'default'
        endpoint = 'PJSIP/abcd'
        context_mock = Mock(name=context, tenant_uuid='fake-tenant')
        self.context_dao.get.return_value = context_mock

        self.agent_status_dao.get_status.return_value = None
        self.agent_status_dao.is_extension_in_use.return_value = False

        self.line_dao.get_interfaces_from_exten_and_context.return_value = [endpoint]

        self.login_manager.login_agent(agent, extension, context, endpoint)

        self.login_action.login_agent.assert_called_once_with(
            agent, extension, context, endpoint
        )

    def test_login_agent_with_invalid_endpoint(self):
        agent = Mock(tenant_uuid='fake-tenant')
        extension = '1001'
        context = 'default'
        endpoint = 'PJSIP/ijkl'
        existing_endpoints = ['PJSIP/abcd', 'PJSIP/efgh']
        context_mock = Mock(name=context, tenant_uuid='fake-tenant')
        self.context_dao.get.return_value = context_mock
        self.agent_status_dao.get_status.return_value = None
        self.agent_status_dao.is_extension_in_use.return_value = False

        self.line_dao.get_interfaces_from_exten_and_context.return_value = (
            existing_endpoints
        )
        self.assertRaises(
            NoSuchExtensionError,
            self.login_manager.login_agent,
            agent,
            extension,
            context,
            endpoint,
        )

        self.login_action.login_agent.assert_not_called()
