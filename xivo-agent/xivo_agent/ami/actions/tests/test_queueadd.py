# -*- coding: UTF-8 -*-

# Copyright (C) 2013  Avencall
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

from mock import patch
from xivo_agent.ami.actions.queueadd import QueueAddAction


class TestQueueAddAction(unittest.TestCase):

    @patch('xivo_agent.ami.actions.queueadd.BaseAction')
    def test_queue_add_action(self, mock_base_action):
        queue = 'queue1001'
        interface = 'Local/1@foobar'
        member_name = 'Agent/234'
        state_interface = 'SIP/abcdef'

        action = QueueAddAction(queue, interface, member_name, state_interface)

        self.assertTrue(action is not None)
        mock_base_action.assert_called_once_with('QueueAdd', [
            ('Queue', queue),
            ('Interface', interface),
            ('MemberName', member_name),
            ('StateInterface', state_interface),
        ])
