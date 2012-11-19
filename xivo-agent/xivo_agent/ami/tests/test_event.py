# -*- coding: UTF-8 -*-

import unittest
from xivo_agent.ami.parser import parse_msg


class TestResponse(unittest.TestCase):

    def test_parse_response(self):
        data = 'Event: foo'

        event = parse_msg(data)

        self.assertEqual('foo', event.name)
        self.assertEqual(None, event.action_id)

    def test_parse_response_with_action_id(self):
        data = 'Event: foo\r\nActionID: bar'

        event = parse_msg(data)

        self.assertEqual('foo', event.name)
        self.assertEqual('bar', event.action_id)
