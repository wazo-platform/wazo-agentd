# -*- coding: UTF-8 -*-

import unittest
from mock import Mock
from xivo_agent.ctl import error
from xivo_agent.service.steps import GetQueueStep


class TestGetQueueStep(unittest.TestCase):

    def test_execute_when_queue_exist(self):
        command = Mock()
        command.queue_id = 12
        response = Mock()
        blackboard = Mock()

        queue_name = 'queue1'
        queue_dao = Mock()
        queue_dao.queue_name.return_value = queue_name

        step = GetQueueStep(queue_dao)
        step.execute(command, response, blackboard)

        queue_dao.queue_name.assert_called_once_with(command.queue_id)
        self.assertEqual(blackboard.queue.name, queue_name)

    def test_execute_when_queue_doesnt_exit(self):
        command = Mock()
        command.queue_id = 12
        response = Mock()
        blackboard = Mock()

        queue_dao = Mock()
        queue_dao.queue_name.side_effect = LookupError()

        step = GetQueueStep(queue_dao)
        step.execute(command, response, blackboard)

        queue_dao.queue_name.assert_called_once_with(command.queue_id)
        self.assertEqual(response.error, error.NO_SUCH_QUEUE)
