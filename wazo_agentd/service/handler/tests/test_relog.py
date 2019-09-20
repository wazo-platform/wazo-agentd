# Copyright 2013-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from mock import Mock
from wazo_agentd.service.manager.relog import RelogManager
from wazo_agentd.service.handler.relog import RelogHandler


class TestRelogHandler(unittest.TestCase):
    def setUp(self):
        self.relog_manager = Mock(RelogManager)
        self.agent_status_dao = Mock()
        self.relog_handler = RelogHandler(self.relog_manager)
        self.tenants = ['fake-tenant']

    def test_handle_relog_all(self):
        self.relog_handler.handle_relog_all(tenant_uuids=self.tenants)

        self.relog_manager.relog_all_agents.assert_called_once_with(
            tenant_uuids=self.tenants
        )
