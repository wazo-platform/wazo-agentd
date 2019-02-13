# Copyright 2013-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from xivo_agent.service import helper


class TestHelper(unittest.TestCase):

    def test_format_agent_member_name(self):
        agent_number = '1000'
        expected = "Agent/1000"

        result = helper.format_agent_member_name(agent_number)
        self.assertEqual(result, expected)

    def test_format_agent_skills(self):
        agent_id = 42
        expected = "agent-42"

        result = helper.format_agent_skills(agent_id)
        self.assertEqual(result, expected)
