# -*- coding: UTF-8 -*-

import unittest
from mock import Mock
from xivo_agent.service.steps import GetLoggedInAgentsStep


class TestGetLoggedInAgentsStep(unittest.TestCase):

    def test_execute(self):
        command = Mock()
        response = Mock()
        blackboard = Mock()

        agent_login_dao = Mock()
        agent_dao = Mock()

        status1 = Mock()
        status2 = Mock()

        agent1 = Mock()
        agent2 = Mock()

        agent_login_dao.get_statuses.return_value = [status1, status2]
        agent_dao.agent_with_id.side_effect = [agent1, agent2]

        step = GetLoggedInAgentsStep(agent_login_dao, agent_dao)
        step.execute(command, response, blackboard)

        expected = [(agent1, status1), (agent2, status2)]

        agent_login_dao.get_statuses.assert_called_once()
        self.assertEqual(blackboard.logged_in_agents, expected)
