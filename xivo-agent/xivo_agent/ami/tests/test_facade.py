# -*- coding: UTF-8 -*-

import unittest
from mock import Mock, patch
from xivo_agent.ami.facade import FacadeAMIClient


class TestFacade(unittest.TestCase):

    @patch('xivo_agent.ami.client.AMIClient')
    @patch('xivo_agent.ami.actions.LoginAction')
    def test_new(self, amiclient, login_action):
        facade = FacadeAMIClient('foo', '1', '2')
        facade._ami_client = Mock()

        facade.db_del('foo', 'bar')

        self.assertTrue(facade._ami_client.execute.called)
