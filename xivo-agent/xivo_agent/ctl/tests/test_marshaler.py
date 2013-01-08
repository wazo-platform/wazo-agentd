# -*- coding: UTF-8 -*-

# Copyright (C) 2012-2013  Avencall
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

from mock import Mock
from xivo_agent.ctl.marshaler import Marshaler
from xivo_agent.ctl.response import CommandResponse


class TestMarshaler(unittest.TestCase):

    def test_marshal_command(self):
        command = Mock()
        command.name = 'foobar'
        command.marshal.return_value = {'a': 1}

        marshal = Marshaler({})

        result = marshal.marshal_command(command)

        command.marshal.assert_called_once_with()
        self.assertEquals(result, ('{"cmd": {"a": 1}, "name": "foobar"}'))

    def test_marshal_response(self):
        response = Mock()
        response.marshal.return_value = {'value': 'success', 'error': None}

        marshal = Marshaler({})

        result = marshal.marshal_response(response)

        response.marshal.assert_called_once_with()
        self.assertEquals(result, '{"value": "success", "error": null}')

    def test_unmarshal_command(self):
        json = '{"name": "foobar", "cmd": {"a":1}}'

        command = Mock()
        registry = {'foobar': command}

        marshal = Marshaler(registry)
        marshal.unmarshal_command(json)

        command.unmarshal.assert_called_once_with({'a': 1})

    def test_unmarshal_response(self):
        json = '{"error": null, "value": "foobar"}'

        marshal = Marshaler({})
        result = marshal.unmarshal_response(json)

        self.assertTrue(isinstance(result, CommandResponse))
        self.assertEquals(result.value, 'foobar')
        self.assertEquals(result.error, None)


if __name__ == "__main__":
    unittest.main()
