# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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

from ..response import CommandResponse


class TestResponse(unittest.TestCase):

    def test_marshal_with_value(self):
        value = {
            'agent_number': '1000',
            'extension': '2000',
            'context': 'default'
        }
        expected = {
            'error': None,
            'value': {
                'agent_number': '1000',
                'extension': '2000',
                'context': 'default'
            }
        }

        response = CommandResponse(value=value)
        result = response.marshal()

        self.assertEquals(result, expected)

    def test_marshal_with_error(self):
        error = 'error message'
        expected = {
            'error': 'error message',
            'value': None
        }

        response = CommandResponse(error=error)
        result = response.marshal()
        self.assertEquals(result, expected)

    def test_unmarshal_with_value_message(self):
        msg = {
            'error': None,
            'value': {
                'agent_number': '1000',
                'extension': '2000',
                'context': 'default'
            }
        }

        response = CommandResponse.unmarshal(msg)

        self.assertEquals(response.value, msg['value'])
        self.assertEquals(response.error, None)

    def test_unmarshal_with_error_message(self):
        msg = {
            'error': 'error message',
            'value': None
        }

        response = CommandResponse.unmarshal(msg)

        self.assertEquals(response.value, None)
        self.assertEquals(response.error, 'error message')
