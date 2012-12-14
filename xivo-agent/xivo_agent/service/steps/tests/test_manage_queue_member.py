# -*- coding: UTF-8 -*-

import unittest
from mock import Mock
from xivo_agent.service.steps import InsertAgentIntoQueuememberStep
from xivo_agent.service.steps.manage_queue_member import DeleteAgentFromQueuememberStep


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


class TestDeleteAgentFromQueuememberStep(unittest.TestCase):

    def setUp(self):
        self.command = Mock()
        self.response = Mock()
        self.response.error = None
        self.blackboard = Mock()
        self.blackboard.queue.name = 'foobar1'
        self.blackboard.agent.id = 123

    def test_execute(self):
        queue_member_dao = Mock()

        step = DeleteAgentFromQueuememberStep(queue_member_dao)
        step.execute(self.command, self.response, self.blackboard)

        queue_member_dao.remove_agent_from_queue.assert_called_once_with(self.blackboard.agent.id,
                                                                         self.blackboard.queue.name)
