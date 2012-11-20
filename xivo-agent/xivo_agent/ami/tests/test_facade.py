# -*- coding: UTF-8 -*-

# Copyright (C) 2012  Avencall
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
