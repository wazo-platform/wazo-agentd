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
from xivo_agent.service.manager.on_agent_updated import OnAgentUpdatedManager, \
    QueueDelta


class TestQueueDelta(unittest.TestCase):

    def setUp(self):
        self.queue1 = Mock()
        self.queue1.id = 1
        self.queue1.name = 'q1'
        self.queue2 = Mock()
        self.queue2.id = 2
        self.queue2.name = 'q2'
        self.old_queue3 = Mock()
        self.old_queue3.id = 3
        self.old_queue3.name = 'q3'
        self.old_queue3.penalty = 0
        self.new_queue3 = Mock()
        self.new_queue3.id = 3
        self.new_queue3.name = 'q3'
        self.new_queue3.penalty = 1
        self.queue4 = Mock()
        self.queue4.id = 4
        self.queue4.name = 'q4'
        self.queue4.penalty = 0

    def test_calculate(self):
        old_queues = [self.queue1, self.old_queue3, self.queue4]
        new_queues = [self.queue2, self.new_queue3, self.queue4]

        delta = QueueDelta.calculate(old_queues, new_queues)

        self.assertEqual(delta.added, [self.queue2])
        self.assertEqual(delta.removed, [self.queue1])
        self.assertEqual(delta.penalty_updated, [self.new_queue3])


class TestOnAgentUpdatedManager(unittest.TestCase):

    def setUp(self):
        step_factory = Mock(StepFactory)

        self.get_agent_status = Mock()
        self.get_agent = Mock()
        self.add_agent_to_queue = Mock()
        self.remove_agent_from_queue = Mock()
        self.update_agent_penalty = Mock()
        self.update_agent_status = Mock()

        step_factory.get_agent_status.return_value = self.get_agent_status
        step_factory.get_agent.return_value = self.get_agent
        step_factory.add_agent_to_queue.return_value = self.add_agent_to_queue
        step_factory.remove_agent_from_queue.return_value = self.remove_agent_from_queue
        step_factory.update_agent_penalty.return_value = self.update_agent_penalty
        step_factory.update_agent_status.return_value = self.update_agent_status

        self.on_agent_updated_manager = OnAgentUpdatedManager(step_factory)

    def test_on_agent_updated(self):
        old_queue = Mock()
        old_queue.name = 'queue1'

        new_queue = Mock()
        new_queue.name = 'queue2'

        updated_queue_before = Mock()
        updated_queue_before.id = 42
        updated_queue_before.name = 'q3'
        updated_queue_before.penalty = 61
        updated_queue_after = Mock()
        updated_queue_after.id = 42
        updated_queue_after.name = 'q3'
        updated_queue_after.penalty = 39

        agent_status = Mock()
        agent_status.agent_id = 1
        agent_status.agent_number = '42'
        agent_status.queues = [old_queue, updated_queue_before]

        agent = Mock()
        agent.id = agent_status.agent_id
        agent.queues = [new_queue, updated_queue_after]

        self.get_agent_status.get_status.return_value = agent_status
        self.get_agent.get_agent_with_id.return_value = agent

        self.on_agent_updated_manager.on_agent_updated(agent_status.agent_id)

        self.get_agent_status.get_status.assert_called_once_with(agent_status.agent_id)
        self.get_agent.get_agent_with_id.assert_called_once_with(agent_status.agent_id)

        # added
        self.add_agent_to_queue.add_agent_to_queue.assert_called_once_with(agent_status, new_queue.name)
        self.update_agent_status.add_agent_to_queue.assert_called_once_with(agent_status.agent_id, new_queue)

        # removed
        self.remove_agent_from_queue.remove_agent_from_queue.assert_called_once_with(agent_status, old_queue.name)
        self.update_agent_status.remove_agent_from_queue.assert_called_once_with(agent_status.agent_id, old_queue.id)

        # penalty updated
        self.update_agent_penalty.update_agent_penalty.assert_called_once_with(agent_status, updated_queue_after)
        self.update_agent_status.update_agent_penalty.assert_called_once_with(agent_status.agent_id, updated_queue_after)
