# -*- coding: UTF-8 -*-

import unittest
from mock import Mock, patch
from xivo_agent.service.factory import StepFactory


class TestStepFactory(unittest.TestCase):

    def setUp(self):
        self.ami_client = Mock()
        self.queue_log_manager = Mock()
        self.agent_login_dao = Mock()
        self.agent_dao = Mock()
        self.line_dao = Mock()
        self.queue_dao = Mock()
        self.queue_member_dao = Mock()
        self.step_factory = StepFactory(self.ami_client,
                                        self.queue_log_manager,
                                        self.agent_login_dao,
                                        self.agent_dao,
                                        self.line_dao,
                                        self.queue_dao,
                                        self.queue_member_dao)

    @patch('xivo_agent.service.steps.GetQueueStep')
    def test_get_queue(self, GetQueueStep):
        self.step_factory.get_queue()

        GetQueueStep.assert_called_once_with(self.queue_dao)

    @patch('xivo_agent.service.steps.GetInterfaceStep')
    def test_get_interface(self, GetInterfaceStep):
        self.step_factory.get_interface()

        GetInterfaceStep.assert_called_once_with()

    @patch('xivo_agent.service.steps.CheckAgentIsNotMemberOfQueueStep')
    def test_check_agent_is_not_member_of_queue(self, CheckAgentIsNotMemberOfQueueStep):
        self.step_factory.check_agent_is_not_member_of_queue()

        CheckAgentIsNotMemberOfQueueStep.assert_called_once_with()

    @patch('xivo_agent.service.steps.InsertAgentIntoQueuememberStep')
    def test_insert_agent_into_queuemember(self, InsertAgentIntoQueuememberStep):
        self.step_factory.insert_agent_into_queuemember()

        InsertAgentIntoQueuememberStep.assert_called_once_with(self.queue_member_dao)

    @patch('xivo_agent.service.steps.AddAgentToQueueStep')
    def test_add_agent_to_queue(self, AddAgentToQueueStep):
        self.step_factory.add_agent_to_queue()

        AddAgentToQueueStep.assert_called_once_with(self.ami_client)
