# -*- coding: UTF-8 -*-

import unittest
from xivo_agent.ctl.commands import LoginCommand


class TestCommands(unittest.TestCase):

    def test_marshal_unmarshal_login(self):
        agent_number = 1
        interface = 'Local/123@foo'
        expected = {'number': agent_number, 'interface': interface}

        data = LoginCommand(agent_number, interface).marshal()

        self.assertEqual(expected, data)

        cmd = LoginCommand.unmarshal(data)

        self.assertEqual(cmd.agent_number, agent_number)
        self.assertEqual(cmd.interface, interface)
