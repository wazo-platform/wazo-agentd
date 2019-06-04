# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from mock import Mock
from wazo_agent.service.manager.on_agent_updated import OnAgentUpdatedManager, \
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
        self.add_to_queue_action = Mock()
        self.remove_from_queue_action = Mock()
        self.update_penalty_action = Mock()
        self.agent_status_dao = Mock()
        self.on_agent_updated_manager = OnAgentUpdatedManager(self.add_to_queue_action,
                                                              self.remove_from_queue_action,
                                                              self.update_penalty_action,
                                                              self.agent_status_dao)

    def test_on_agent_updated(self):
        old_queue = Mock()
        old_queue.id = 1
        new_queue = Mock()
        new_queue.id = 2
        updated_queue_before = Mock()
        updated_queue_before.id = 3
        updated_queue_before.penalty = 61
        updated_queue_after = Mock()
        updated_queue_after.id = 3
        updated_queue_after.penalty = 39

        agent_id = 1
        agent = Mock()
        agent.id = agent_id
        agent.queues = [new_queue, updated_queue_after]
        agent_status = Mock()
        agent_status.agent_id = agent_id
        agent_status.queues = [old_queue, updated_queue_before]

        self.agent_status_dao.get_status.return_value = agent_status

        self.on_agent_updated_manager.on_agent_updated(agent)

        self.add_to_queue_action.add_agent_to_queue.assert_called_once_with(agent_status, new_queue)
        self.remove_from_queue_action.remove_agent_from_queue.assert_called_once_with(agent_status, old_queue)
        self.update_penalty_action.update.assert_called_once_with(agent_status, updated_queue_after)
