# Copyright 2013-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import patch
from xivo_agent.ami.actions.queueadd import QueueAddAction


class TestQueueAddAction(unittest.TestCase):

    @patch('xivo_agent.ami.actions.queueadd.BaseAction')
    def test_queue_add_action(self, mock_base_action):
        queue = 'queue1001'
        interface = 'Local/1@foobar'
        member_name = 'Agent/234'
        state_interface = 'PJSIP/abcdef'
        penalty = '1'
        skills = 'agent-12'

        action = QueueAddAction(queue, interface, member_name, state_interface, penalty, skills)

        self.assertTrue(action is not None)
        mock_base_action.assert_called_once_with('QueueAdd', [
            ('Queue', queue),
            ('Interface', interface),
            ('MemberName', member_name),
            ('StateInterface', state_interface),
            ('Penalty', penalty),
            ('Skills', skills)
        ])
