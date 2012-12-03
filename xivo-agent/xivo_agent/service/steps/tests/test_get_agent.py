# -*- coding: UTF-8 -*-

import unittest
from mock import Mock
from xivo_agent.service.steps import GetAgentStep


class TestGetAgentStep(unittest.TestCase):

    def test_execute(self):
        command = Mock()
        command.agent_id = 12
        response = Mock()
        blackboard = Mock()

        agent = Mock()
        agentfeatures_dao = Mock()
        agentfeatures_dao.agent_with_id.return_value = agent

        step = GetAgentStep(agentfeatures_dao)
        step.execute(command, response, blackboard)

        agentfeatures_dao.agent_with_id.assert_called_once_with(command.agent_id)
        self.assertEqual(blackboard.agent, agent)
