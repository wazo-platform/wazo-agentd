# -*- coding: UTF-8 -*-

import datetime
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
        self.agent_login_dao.is_extension_in_use.return_value = False
        self.agent_features_dao = Mock()

        self.service = AgentService(self.ami_client,
                                    self.agent_server,
                                    self.queue_log_manager,
                                    self.agent_login_dao,
                                    self.agent_features_dao)

    def test_login_cmd_when_logged_off(self):
        login_cmd = self._new_login_cmd(1, '1001', 'default')
        agent = self._new_agent(1, number='11')
        self._setup_dao(agent)

        response = self._new_response()

        self.service._exec_login_cmd(login_cmd, response)

        self.agent_login_dao.log_in_agent.assert_called_with(1, '1001', 'default')
        self.queue_log_manager.on_agent_logged_in.assert_called_with('11', '1001', 'default')

    def test_login_cmd_second_agent(self):
        login_cmd = self._new_login_cmd(2, '1002', 'othercontext')
        agent = self._new_agent(2)
        self._setup_dao(agent)

        response = self._new_response()

        self.service._exec_login_cmd(login_cmd, response)

        self.agent_login_dao.log_in_agent.assert_called_with(2, '1002', 'othercontext')

    def test_login_cmd_same_agent_twice(self):
        login_cmd = self._new_login_cmd(1)
        agent = self._new_agent(1)
        self._setup_dao(agent, True)

        response = self._new_response()

        self.service._exec_login_cmd(login_cmd, response)

        self.agent_login_dao.is_agent_logged_in.assert_called_with(login_cmd.agent_id)

    def test_login_cmd_set_error_to_already_logged_when_already_logged_in(self):
        login_cmd = self._new_login_cmd(1)
        agent = self._new_agent(1)
        self._setup_dao(agent, True)

        response = self._new_response()

        self.service._exec_login_cmd(login_cmd, response)

        self.assertEqual(error.ALREADY_LOGGED, response.error)
        self.agent_login_dao.is_agent_logged_in.assert_called_with(login_cmd.agent_id)

    def test_login_cmd_set_error_to_already_logged_when_logging_on_different_interface(self):
        login_cmd = self._new_login_cmd(1, '1002', 'default')
        agent = self._new_agent(1)
        self._setup_dao(agent, True)

        response = self._new_response()

        self.service._exec_login_cmd(login_cmd, response)

        self.assertEqual(error.ALREADY_LOGGED, response.error)
        self.agent_login_dao.is_agent_logged_in.assert_called_with(login_cmd.agent_id)

    def test_login_cmd_cant_logged_two_agents_on_same_extension(self):
        agent = self._new_agent(1)
        login_cmd = self._new_login_cmd(agent.id, '1001', 'default')
        response = self._new_response()
        self.agent_features_dao.agent_with_id.return_value = agent
        self.agent_login_dao.is_agent_logged_in.return_value = False
        self.agent_login_dao.is_extension_in_use.return_value = True

        self.service._exec_login_cmd(login_cmd, response)

        self.assertEqual(error.ALREADY_IN_USE, response.error)

    def test_logoff_cmd_when_logged_in(self):
        logged_time = 10
        dt_login_at = datetime.datetime(2012, 1, 1)
        dt_now = dt_login_at + datetime.timedelta(seconds=logged_time)
        with patch('datetime.datetime') as datetime_mock:
            datetime_mock.now.return_value = dt_now
            logoff_cmd = self._new_logoff_cmd(1)
            agent = self._new_agent(1, number='11', queues=[self._new_queue('1201')])
            self._setup_dao(agent, True)

            agent_login_status = Mock()
            agent_login_status.login_at = dt_login_at
            agent_login_status.extension = '1001'
            agent_login_status.context = 'default'
            self.agent_login_dao.get_status.return_value = agent_login_status

            response = Mock()

            self.service._exec_logoff_cmd(logoff_cmd, response)

            self.agent_login_dao.is_agent_logged_in.assert_called_with(logoff_cmd.agent_id)
            self.agent_login_dao.get_status.assert_called_with(logoff_cmd.agent_id)
            self.ami_client.queue_remove.assert_called_with('1201', 'Local/1001@default')
            self.queue_log_manager.on_agent_logged_off.assert_called_with('11', '1001', 'default', logged_time)
            self.agent_login_dao.log_off_agent.assert_called_with(logoff_cmd.agent_id)

    def test_logoff_cmd_set_error_to_not_logged_when_agent_not_logged(self):
        logoff_cmd = self._new_logoff_cmd(1)
        agent = self._new_agent(1)
        self._setup_dao(agent, False)

        response = self._new_response()

        self.service._exec_logoff_cmd(logoff_cmd, response)

        self.agent_login_dao.is_agent_logged_in.assert_called_with(logoff_cmd.agent_id)
        self.assertEqual(error.NOT_LOGGED, response.error)

    def test_status_cmd_when_logged_in(self):
        agent_id = 1
        status_cmd = self._new_status_cmd(agent_id)
        self.agent_login_dao.is_agent_logged_in.return_value = True

        expected = {'logged': True}

        response = self._new_response()

        self.service._exec_status_cmd(status_cmd, response)

        self.assertEqual(expected, response.value)
        self.agent_login_dao.is_agent_logged_in.assert_called_with(status_cmd.agent_id)

    def test_status_cmd_when_logged_off(self):
        agent_id = 1
        status_cmd = self._new_status_cmd(agent_id)
        self.agent_login_dao.is_agent_logged_in.return_value = False

        expected = {'logged': False}

        response = self._new_response()

        self.service._exec_status_cmd(status_cmd, response)

        self.assertEqual(expected, response.value)
        self.agent_login_dao.is_agent_logged_in.assert_called_with(status_cmd.agent_id)

    def _new_login_cmd(self, agent_id, extension='1001', context='default'):
        login_cmd = Mock()
        login_cmd.agent_id = agent_id
        login_cmd.extension = extension
        login_cmd.context = context
        return login_cmd

    def _new_logoff_cmd(self, agent_id):
        logoff_cmd = Mock()
        logoff_cmd.agent_id = 1
        return logoff_cmd

    def _new_status_cmd(self, agent_id):
        status_cmd = Mock()
        status_cmd.agent_id = agent_id
        return status_cmd

    def _new_agent(self, agent_id, number=None, queues=None):
        if number is None:
            number = str(agent_id)
        if queues is None:
            queues = []
        agent = Mock()
        agent.id = agent_id
        agent.number = number
        agent.queues = queues
        return agent

    def _new_queue(self, name):
        queue = Mock()
        queue.name = name
        return queue

    def _new_response(self):
        response = Mock()
        response.error = False
        return response

    def _setup_dao(self, agent, logged_in=False):
        self.agent_features_dao.agent_with_id.return_value = agent
        self.agent_login_dao.is_agent_logged_in.return_value = logged_in
