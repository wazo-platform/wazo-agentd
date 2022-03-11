# Copyright 2013-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from wazo_agentd.service import helper


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

    def test_is_valid_agent_number(self):
        valid_numbers = ['0', '1234567890']
        invalid_numbers = ['a', '1234a4567890', '', ' ']

        for valid_number in valid_numbers:
            self.assertTrue(helper.is_valid_agent_number(valid_number))

        for invalid_number in invalid_numbers:
            self.assertFalse(helper.is_valid_agent_number(invalid_number))
