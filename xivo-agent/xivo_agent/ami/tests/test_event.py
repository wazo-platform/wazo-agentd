# -*- coding: utf-8 -*-

# Copyright (C) 2012-2014 Avencall
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

from hamcrest import assert_that, equal_to
import unittest
from xivo_agent.ami.event import Event


class TestEvent(unittest.TestCase):

    def setUp(self):
        headers = {'ze_field': 'ze_value', 'ze_other_field': 'ze_other_value'}
        self.event = Event('name', 'action_id', headers)

    def test_given_event_then_name_and_action_id(self):
        assert_that(self.event.name, equal_to('name'))
        assert_that(self.event.action_id, equal_to('action_id'))

    def test_given_event_when_get_value_then_value_returned(self):
        value = self.event.get_value('ze_field')

        assert_that(value, equal_to('ze_value'))
