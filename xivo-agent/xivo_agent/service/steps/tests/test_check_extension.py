# -*- coding: UTF-8 -*-

import unittest
from mock import Mock
from xivo_agent.ctl import error
from xivo_agent.service.steps import CheckExtensionIsNotInUseStep


class TestCheckExtensionIsNotInUseStep(unittest.TestCase):

    def test_execute_when_not_in_use(self):
        command = Mock()
        response = Mock()
        response.error = None
        blackboard = Mock()
        blackboard.extension = '1001'
        blackboard.context = 'default'

        agent_login_dao = Mock()
        agent_login_dao.is_extension_in_use.return_value = False

        step = CheckExtensionIsNotInUseStep(agent_login_dao)
        step.execute(command, response, blackboard)

        agent_login_dao.is_extension_in_use.assert_called_once_with(blackboard.extension, blackboard.context)
        self.assertEqual(response.error, None)

    def test_execute_when_in_use(self):
        command = Mock()
        response = Mock()
        response.error = None
        blackboard = Mock()
        blackboard.extension = '1001'
        blackboard.context = 'default'

        agent_login_dao = Mock()
        agent_login_dao.is_extension_in_use.return_value = True

        step = CheckExtensionIsNotInUseStep(agent_login_dao)
        step.execute(command, response, blackboard)

        agent_login_dao.is_extension_in_use.assert_called_once_with(blackboard.extension, blackboard.context)
        self.assertEqual(response.error, error.ALREADY_IN_USE)
