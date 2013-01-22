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
from xivo_agent.service.steps import GetAgentStep


class TestGetAgentStep(unittest.TestCase):

    def test_execute(self):
        command = Mock()
        command.agent_id = 12
        response = Mock()
        blackboard = Mock()

        agent = Mock()
        agent_dao = Mock()
        agent_dao.agent_with_id.return_value = agent

        step = GetAgentStep(agent_dao)
        step.execute(command, response, blackboard)

        agent_dao.agent_with_id.assert_called_once_with(command.agent_id)
        self.assertEqual(blackboard.agent, agent)
