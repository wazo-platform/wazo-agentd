# Copyright 2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock

from wazo_agentd.service.manager.on_agent_deleted import OnAgentDeletedManager


class TestOnAgentDeletedManager(unittest.TestCase):
    def setUp(self):
        self.logoff_action = Mock()
        self.agent_status_dao = Mock()
        self.on_agent_deleted_manager = OnAgentDeletedManager(
            self.logoff_action,
            self.agent_status_dao,
        )

    def test_on_agent_deleted_logged_agent(self):
        agent_id = 10
        agent_status = Mock(agent_id=agent_id)
        self.agent_status_dao.get_agent_login_status_by_id_for_logoff.return_value = (
            agent_status
        )

        self.on_agent_deleted_manager.on_agent_deleted(agent_id)

        self.logoff_action.logoff_agent.assert_called_once_with(agent_status)
        self.agent_status_dao.remove_agent_from_all_queues.assert_called_once_with(
            agent_id
        )

    def test_on_agent_deleted_agent_not_logged(self):
        agent_id = 10
        self.agent_status_dao.get_agent_login_status_by_id_for_logoff.return_value = (
            None
        )

        self.on_agent_deleted_manager.on_agent_deleted(agent_id)

        self.logoff_action.logoff_agent.assert_not_called()
        self.agent_status_dao.remove_agent_from_all_queues.assert_called_once_with(
            agent_id
        )
