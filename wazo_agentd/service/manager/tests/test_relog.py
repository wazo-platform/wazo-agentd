# Copyright 2013-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock

from wazo_agentd.service.action.login import LoginAction
from wazo_agentd.service.action.logoff import LogoffAction
from wazo_agentd.service.manager.relog import RelogManager


class TestRelogManager(unittest.TestCase):
    def setUp(self):
        self.login_action = Mock(LoginAction)
        self.logoff_action = Mock(LogoffAction)
        self.agent_status_dao = Mock()
        self.agent_dao = Mock()
        self.relog_manager = RelogManager(
            self.login_action, self.logoff_action, self.agent_dao, self.agent_status_dao
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

    def test_relog_all_agents_all_queues(self):
        agent_id = 42
        agent = Mock()
        agent.id = agent_id
        agent.queues = [Mock(), Mock()]
        agent_status = Mock()
        agent_status.agent_id = agent_id

        self.agent_dao.get_agent.return_value = agent
        self.agent_status_dao.get_logged_agent_ids.return_value = [agent_id]
        self.agent_status_dao.get_status.return_value = agent_status

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
