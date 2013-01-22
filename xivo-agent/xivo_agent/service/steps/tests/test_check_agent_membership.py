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
from xivo_agent.ctl import error
from xivo_agent.service.steps import CheckAgentIsNotMemberOfQueueStep
from xivo_agent.service.steps.check_agent_membership import CheckAgentIsMemberOfQueueStep


class TestCheckAgentIsMemberOfQueueStep(unittest.TestCase):

    def setUp(self):
        self.command = Mock()
        self.response = Mock()
        self.response.error = None
        self.blackboard = Mock()
        self.blackboard.queue.name = 'foobar1'

    def test_execute_when_is_member(self):
        agent_queue = Mock()
        agent_queue.name = 'foobar1'
        self.blackboard.agent.queues = [agent_queue]

        step = CheckAgentIsMemberOfQueueStep()
        step.execute(self.command, self.response, self.blackboard)

        self.assertEqual(self.response.error, None)

    def test_execute_when_is_not_member(self):
        self.blackboard.agent.queues = []

        step = CheckAgentIsMemberOfQueueStep()
        step.execute(self.command, self.response, self.blackboard)

        self.assertEqual(self.response.error, error.NOT_IN_QUEUE)


class TestCheckAgentIsNotMemberOfQueueStep(unittest.TestCase):

    def setUp(self):
        self.command = Mock()
        self.response = Mock()
        self.response.error = None
        self.blackboard = Mock()
        self.blackboard.queue.name = 'foobar1'

    def test_execute_when_is_not_member(self):
        self.blackboard.agent.queues = []

        step = CheckAgentIsNotMemberOfQueueStep()
        step.execute(self.command, self.response, self.blackboard)

        self.assertEqual(self.response.error, None)

    def test_execute_when_is_member(self):
        agent_queue = Mock()
        agent_queue.name = 'foobar1'
        self.blackboard.agent.queues = [agent_queue]

        step = CheckAgentIsNotMemberOfQueueStep()
        step.execute(self.command, self.response, self.blackboard)

        self.assertEqual(self.response.error, error.ALREADY_IN_QUEUE)
