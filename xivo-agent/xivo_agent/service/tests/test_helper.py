# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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
