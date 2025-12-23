# Copyright 2013-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock

from wazo_agentd.service.manager.on_agent_updated import OnAgentUpdatedManager


class TestOnAgentUpdatedManager(unittest.TestCase):
    def setUp(self):
        self.update_penalty_action = Mock(update=Mock())
        self.agent_status_dao = Mock()
        self.on_agent_updated_manager = OnAgentUpdatedManager(
            self.update_penalty_action,
            self.agent_status_dao,
        )

    def test_on_agent_updated(self):
        queue_updated = Mock(id=1, penalty=61)
        original_queue = Mock(id=1, penalty=37)
        original_queue._replace = Mock(
            side_effect=lambda penalty: Mock(id=1, penalty=penalty)
        )

        agent = Mock(id=42, queues=[queue_updated])
        agent_status = Mock(agent_id=42, queues=[original_queue])

        self.agent_status_dao.get_status.return_value = agent_status

        self.on_agent_updated_manager.on_agent_updated(agent)

        self.update_penalty_action.update.assert_called()
        (arg1, arg2), _ = self.update_penalty_action.update.call_args

        assert arg1 is agent_status
        assert arg2.id == 1 and arg2.penalty == queue_updated.penalty
