# -*- coding: UTF-8 -*-

import unittest
from mock import Mock, patch
from xivo_agent.service import AgentService
from xivo_agent.ctl import error

class TestService(unittest.TestCase):

    def setUp(self):
        self.ami_client = Mock()
        self.agent_server = Mock()
        self.queue_log_manager = Mock()
        self.agent_login_dao = Mock()

        self.service = AgentService(self.ami_client, self.agent_server,
                                    self.queue_log_manager, self.agent_login_dao)


    @patch('xivo_agent.dao.agent_with_id')
    def test_login_cmd(self, dao_agent_with_id):
        login_cmd = self._new_login_cmd(1, '1001', 'default')
        agent = self._new_agent(1)
        self._setup_dao(dao_agent_with_id, agent)

        response = Mock()

        self.service._exec_login_cmd(login_cmd, response)

        self.agent_login_dao.log_in_agent.assert_called_with(1, 'Local/1001@default')

    @patch('xivo_agent.dao.agent_with_id')
    def test_login_cmd_second_agent(self, dao_agent_with_id):
        login_cmd = self._new_login_cmd(2, '1002', 'othercontext')
        agent = self._new_agent(2)
        self._setup_dao(dao_agent_with_id, agent)

        response = Mock()

        self.service._exec_login_cmd(login_cmd, response)

        self.agent_login_dao.log_in_agent.assert_called_with(2, 'Local/1002@othercontext')

    @patch('xivo_agent.dao.agent_with_id')
    def test_login_cmd_same_agent_twice(self, dao_agent_with_id):
        login_cmd = self._new_login_cmd(1)
        agent = self._new_agent(1)
        self._setup_dao(dao_agent_with_id, agent, True)

        response = Mock()

        self.service._exec_login_cmd(login_cmd, response)

        self.agent_login_dao.is_agent_logged_in.assert_called_with(login_cmd.agent_id)

    @patch('xivo_agent.dao.agent_with_id')
    def test_login_cmd_set_error_to_already_logged_when_already_logged_in(self, dao_agent_with_id):
        login_cmd = self._new_login_cmd(1)
        agent = self._new_agent(1)
        self._setup_dao(dao_agent_with_id, agent, True)

        response = Mock()

        self.service._exec_login_cmd(login_cmd, response)

        self.assertEqual(error.ALREADY_LOGGED, response.error)
        self.agent_login_dao.is_agent_logged_in.assert_called_with(login_cmd.agent_id)


        response = Mock()

        self.service._exec_login_cmd(login_cmd, response)

        self.assertEqual(error.ALREADY_LOGGED, response.error)
        self.agent_login_dao.is_agent_logged_in.assert_called_with(login_cmd.agent_id)

    def _new_login_cmd(self, agent_id, extension='1001', context='default'):
        login_cmd = Mock()
        login_cmd.agent_id = agent_id
        login_cmd.extension = extension
        login_cmd.context = context
        return login_cmd

    def _new_agent(self, agent_id):
        agent = Mock()
        agent.id = agent_id
        agent.queues = []
        return agent

    def _setup_dao(self, dao, agent, logged_in=False):
        dao.return_value = agent
        self.agent_login_dao.is_agent_logged_in.return_value = logged_in
