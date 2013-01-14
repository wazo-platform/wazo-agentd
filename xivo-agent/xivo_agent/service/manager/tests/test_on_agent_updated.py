# -*- coding: UTF-8 -*-

# Copyright (C) 2013  Avencall
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
from xivo_agent.service.factory import StepFactory
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

    def test_calculate(self):
        old_queues = [self.queue1]
        new_queues = [self.queue2]

        delta = QueueDelta.calculate(old_queues, new_queues)

        self.assertEqual(delta.added, [self.queue2])
        self.assertEqual(delta.removed, [self.queue1])


class TestOnAgentUpdatedManager(unittest.TestCase):

    def test_on_agent_updated(self):
        step_factory = Mock(StepFactory)

        get_agent_status = Mock()
        get_agent_step = Mock()
        add_agent_to_queue_step = Mock()
        remove_agent_from_queue_step = Mock()
        update_agent_status_step = Mock()

        step_factory.get_agent_status.return_value = get_agent_status
        step_factory.get_agent.return_value = get_agent_step
        step_factory.add_agent_to_queue.return_value = add_agent_to_queue_step
        step_factory.remove_agent_from_queue.return_value = remove_agent_from_queue_step
        step_factory.update_agent_status.return_value = update_agent_status_step

        agent_id = 1
        agent_number = '42'

        old_queue = Mock()
        old_queue.name = 'queue1'

        new_queue = Mock()
        new_queue.name = 'queue2'

        agent_status = Mock()
        agent_status.agent_id = agent_id
        agent_status.agent_number = agent_number
        agent_status.queues = [old_queue]

        agent = Mock()
        agent.id = agent_id
        agent.queues = [new_queue]
        get_agent_status.get_status.return_value = agent_status
        get_agent_step.get_agent_with_id.return_value = agent

        on_agent_updated_manager = OnAgentUpdatedManager(step_factory)

        on_agent_updated_manager.on_agent_updated(agent_id)

        get_agent_status.get_status.assert_called_once_with(agent_id)
        get_agent_step.get_agent_with_id.assert_called_once_with(agent_id)

        # added
        add_agent_to_queue_step.add_agent_to_queue.assert_called_once_with(agent_status, new_queue.name)
        update_agent_status_step.add_agent_to_queue.assert_called_once_with(agent_id, new_queue)

        # removed
        remove_agent_from_queue_step.remove_agent_from_queue.assert_called_once_with(agent_status, old_queue.name)
        update_agent_status_step.remove_agent_from_queue.assert_called_once_with(agent_id, old_queue.id)
