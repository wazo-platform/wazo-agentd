# -*- coding: UTF-8 -*-

# Copyright (C) 2012  Avencall
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
from xivo_agent.ctl.transport import Transport


class TestTransport(unittest.TestCase):

    def test_send_command(self):
        addr = Mock()
        sock = Mock()
        command = Mock()
        command.name = 'foobar'
        command.marshal.return_value = {'a': 1}
        transport = Transport(sock)

        transport.send_command(command, addr)

        command.marshal.assert_called_once_with()
        sock.sendto.assert_called_once_with('{"cmd": {"a": 1}, "name": "foobar"}', addr)

    def test_send_response(self):
        addr = Mock()
        sock = Mock()
        response = Mock()
        response.marshal.return_value = {'error': None, 'value': None}
        transport = Transport(sock)

        transport.send_response(response, addr)

        response.marshal.assert_called_once_with()
        sock.sendto.assert_called_once_with('{"value": null, "error": null}', addr)

    def test_recv_command(self):
        expected_addr = Mock()
        sock = Mock()
        sock.recvfrom.return_value = ('{"cmd": {"a": 1}, "name": "foobar"}', expected_addr)
        FoobarCommand = Mock()
        FoobarCommand.unmarshal.return_value = 'fake'
        transport = Transport(sock)

        command, addr = transport.recv_command({'foobar': FoobarCommand})

        FoobarCommand.unmarshal.assert_called_once_with({'a': 1})
        self.assertEqual('fake', command)
        self.assertEqual(expected_addr, addr)

    def test_recv_response(self):
        sock = Mock()
        sock.recvfrom.return_value = ('{"value": null, "error": null}', Mock())
        transport = Transport(sock)

        response = transport.recv_response()

        self.assertEqual(None, response.error)
        self.assertEqual(None, response.value)
