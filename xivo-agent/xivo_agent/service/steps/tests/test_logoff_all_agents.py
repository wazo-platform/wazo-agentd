# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

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
            send_agent_logoff_step.send_agent_logoff.assert_any_call(status.agent_id, status.agent_number)
