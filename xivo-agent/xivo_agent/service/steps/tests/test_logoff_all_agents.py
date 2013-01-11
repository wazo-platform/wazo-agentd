# -*- coding: UTF-8 -*-

import unittest
from mock import Mock
from xivo_agent.service.steps.manage_queues import RemoveAgentFromQueuesStep
from xivo_agent.service.steps.update_queue_log import UpdateQueueLogStep
from xivo_agent.service.steps.update_agent_status import UpdateAgentStatusStep
from xivo_agent.service.steps.manage_events import SendAgentLogoffEventStep
from xivo_agent.service.steps.logoff_all_agents import LogoffAllAgentsStep


class TestLogoffAllAgentsStep(unittest.TestCase):

    def test_execute(self):

        queue_manager_step = Mock(RemoveAgentFromQueuesStep)
        update_queue_log_step = Mock(UpdateQueueLogStep)
        update_agent_status_step = Mock(UpdateAgentStatusStep)
        send_agent_logoff_step = Mock(SendAgentLogoffEventStep)

        command = Mock()
        response = Mock()
        blackboard = Mock()

        agent1 = Mock()
        agent2 = Mock()
        status1 = Mock()
        status2 = Mock()
        logged_in_agents = [(agent1, status1), (agent2, status2)]

        blackboard.logged_in_agents = logged_in_agents

        logoff_all_agents_step = LogoffAllAgentsStep(
             queue_manager_step,
             update_queue_log_step,
             update_agent_status_step,
             send_agent_logoff_step
        )

        logoff_all_agents_step.execute(command, response, blackboard)

        for agent, status in logged_in_agents:

            queue_manager_step.remove_agent_from_queues.assert_any_call(status)
            update_queue_log_step.log_off_agent.assert_any_call(status)
            update_agent_status_step.log_off_agent.assert_any_call(agent.id)
            send_agent_logoff_step.send_agent_logoff.assert_any_call(agent)
