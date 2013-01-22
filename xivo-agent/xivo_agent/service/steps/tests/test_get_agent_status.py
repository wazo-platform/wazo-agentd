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
