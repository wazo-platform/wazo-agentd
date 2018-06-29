# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from xivo_agent.service import helper


class TestHelper(unittest.TestCase):

    def test_format_agent_member_name(self):
        agent_number = '1000'
        expected = "Agent/1000"

        result = helper.format_agent_member_name(agent_number)
        self.assertEquals(result, expected)

    def test_format_agent_skills(self):
        agent_id = 42
        expected = "agent-42"

        result = helper.format_agent_skills(agent_id)
        self.assertEquals(result, expected)
