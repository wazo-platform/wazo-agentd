# -*- coding: UTF-8 -*-

import unittest
from mock import Mock
from xivo_agent.service.steps import InsertAgentIntoQueuememberStep


class TestInsertAgentIntoQueuememberStep(unittest.TestCase):

    def setUp(self):
        self.command = Mock()
        self.response = Mock()
        self.response.error = None
        self.blackboard = Mock()
        self.blackboard.queue.name = 'foobar1'
        self.blackboard.agent.id = 123
        self.blackboard.agent.number = '456'

    def test_execute(self):
        queue_member_dao = Mock()

        step = InsertAgentIntoQueuememberStep(queue_member_dao)
        step.execute(self.command, self.response, self.blackboard)

        queue_member_dao.add_agent_to_queue.assert_called_once_with(self.blackboard.agent.id,
                                                                    self.blackboard.agent.number,
                                                                    self.blackboard.queue.name)
