# Copyright 2012-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, equal_to
import unittest
from wazo_agentd.ami.event import Event


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
