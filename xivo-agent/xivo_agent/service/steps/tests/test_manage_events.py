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
from xivo_agent.service.steps import SendAgentAddedToQueueEventStep
from xivo_agent.service.steps.manage_events import SendAgentRemovedFromQueueEventStep,\
    SendAgentLogoffEventStep


class TestSendAgentAddedToQueueEventStep(unittest.TestCase):

    def setUp(self):
        self.command = Mock()
        self.response = Mock()
        self.response.error = None
        self.blackboard = Mock()
        self.blackboard.agent.id = 123
        self.blackboard.agent.number = '456'
        self.blackboard.queue.name = 'queue1'

    def test_execute(self):
        agent_client = Mock()

        step = SendAgentAddedToQueueEventStep(agent_client)
        step.execute(self.command, self.response, self.blackboard)

        agent_client.agent_added_to_queue.assert_called_once_with(self.blackboard.agent.id,
                                                                  self.blackboard.agent.number,
                                                                  self.blackboard.queue.name)


class TestSendAgentRemovedFromQueueEventStep(unittest.TestCase):

    def setUp(self):
        self.command = Mock()
        self.response = Mock()
        self.response.error = None
        self.blackboard = Mock()
        self.blackboard.agent.id = 123
        self.blackboard.agent.number = '456'
        self.blackboard.queue.name = 'queue1'

    def test_execute(self):
        agent_client = Mock()

        step = SendAgentRemovedFromQueueEventStep(agent_client)
        step.execute(self.command, self.response, self.blackboard)

        agent_client.agent_removed_from_queue.assert_called_once_with(self.blackboard.agent.id,
                                                                      self.blackboard.agent.number,
                                                                      self.blackboard.queue.name)


class TestSendLogoffEventStep(unittest.TestCase):

    def setUp(self):
        self.command = Mock()
        self.response = Mock()
        self.response.error = None
        self.blackboard = Mock()
        self.blackboard.agent_status.agent_id = 123
        self.blackboard.agent_status.agent_number = '456'

    def test_execute(self):
        agent_client = Mock()

        step = SendAgentLogoffEventStep(agent_client)
        step.execute(self.command, self.response, self.blackboard)

        agent_client.agent_logoff.assert_called_once_with(self.blackboard.agent_status.agent_id,
                                                          self.blackboard.agent_status.agent_number)
