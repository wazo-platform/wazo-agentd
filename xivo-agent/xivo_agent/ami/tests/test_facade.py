# -*- coding: utf-8 -*-

# Copyright (C) 2012-2013 Avencall
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

    @patch('xivo_agent.ami.client.ReconnectingAMIClient')
    def test_new(self, ReconnectingAMIClient):
        facade = FacadeAMIClient('example.org', '1', '2')
        facade._ami_client = Mock()

        facade.db_del('foo', 'bar')

        ReconnectingAMIClient.assert_called_once_with('example.org', 5038, facade._login)
        self.assertTrue(facade._ami_client.execute.called)

    @patch('xivo_agent.ami.client.ReconnectingAMIClient')
    def test_close_call_ami_client_disconnect(self, ReconnectingAMIClient):
        facade = FacadeAMIClient('example.org', '1', '2')
        facade._ami_client = Mock()

        facade.close()

        facade._ami_client.disconnect.assert_called_once_with()
