# Copyright 2013-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from mock import Mock

from wazo_agentd.service.manager.login import LoginManager
from wazo_agentd.exception import ContextDifferentTenantError


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

        self.login_action.login_agent.assert_called_once_with(agent, extension, context)

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
