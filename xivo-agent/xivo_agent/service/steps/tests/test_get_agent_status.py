# -*- coding: UTF-8 -*-

import unittest
from mock import Mock
from xivo_agent.service.steps import GetAgentStatusStep


class TestGetAgentStatusStep(unittest.TestCase):

    def test_execute(self):
        command = Mock()
        response = Mock()
        blackboard = Mock()
        blackboard.agent.id = 12

        agent_status = Mock()
        agent_status_dao = Mock()
        agent_status_dao.get_status.return_value = agent_status

        step = GetAgentStatusStep(agent_status_dao)
        step.execute(command, response, blackboard)

        agent_status_dao.get_status.assert_called_once_with(blackboard.agent.id)
        self.assertEqual(blackboard.agent_status, agent_status)
