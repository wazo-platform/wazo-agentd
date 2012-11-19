# -*- coding: UTF-8 -*-

import unittest
from xivo_agent.ami.parser import parse_msg


class TestResponse(unittest.TestCase):

    def test_parse_response(self):
        data = 'Response: Success\r\nMessage: bar'

        response = parse_msg(data)

        self.assertEqual('Success', response.response)
        self.assertEqual(None, response.action_id)
        self.assertTrue(response.is_success())

    def test_parse_response_with_action_id(self):
        data = 'Response: Success\r\nMessage: bar\r\nActionID: foo'

        response = parse_msg(data)

        self.assertEqual('Success', response.response)
        self.assertEqual('foo', response.action_id)
        self.assertTrue(response.is_success())
