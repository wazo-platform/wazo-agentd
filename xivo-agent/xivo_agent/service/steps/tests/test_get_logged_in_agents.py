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
from mock import Mock, patch
from xivo_agent.service.steps import GetLoggedInAgentsStep


class TestGetLoggedInAgentsStep(unittest.TestCase):

    def test_execute(self):
        command = Mock()
        response = Mock()
        blackboard = Mock()

        agent_status_dao = Mock()
        agent_dao = Mock()

        agent1 = Mock()
        agent2 = Mock()

        status1 = Mock()
        status2 = Mock()

        step = GetLoggedInAgentsStep(agent_status_dao, agent_dao)

        with patch.object(step, '_logged_in_agent_ids') as logged_in_agent_ids:
            with patch.object(step, '_get_agent_and_status') as get_agent_and_status:

                agents_logged_in = [(agent1, status1), (agent2, status2)]
                logged_in_agent_ids.return_value = [1, 2]

                get_agent_and_status.side_effect = [(agent1, status1), (agent2, status2)]
                step.execute(command, response, blackboard)

                self.assertEqual(blackboard.logged_in_agents, agents_logged_in)

    def test_logged_in_agent_ids(self):
        agent_dao = Mock()
        agent_status_dao = Mock()

        status1 = Mock()
        status1.logged = True
        status1.agent_id = 1

        status2 = Mock()
        status2.logged = False
        status2.agent_id = 2

        status3 = Mock()
        status3.logged = True
        status3.agent_id = 3

        agent_status_dao.get_statuses.return_value = [status1, status2, status3]

        step = GetLoggedInAgentsStep(agent_status_dao, agent_dao)
        agent_ids = step._logged_in_agent_ids()
        expected = [1, 3]

        self.assertEquals(list(agent_ids), expected)
        agent_status_dao.get_statuses.assert_called_once()


    def test_get_agent_and_status(self):
        agent_dao = Mock()
        agent_status_dao = Mock()

        agent_id = 1
        agent = Mock()
        status = Mock()

        agent_dao.agent_with_id.return_value = agent
        agent_status_dao.get_status.return_value = status

        step = GetLoggedInAgentsStep(agent_status_dao, agent_dao)
        result = step._get_agent_and_status(agent_id)
        expected = (agent, status)

        self.assertEquals(result, expected)
        agent_dao.agent_with_id.assert_called_once_with(agent_id)
        agent_status_dao.get_status.assert_called_once_with(agent_id)
