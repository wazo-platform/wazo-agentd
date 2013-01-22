# -*- coding: utf-8 -*-

# Copyright (C) 2012-2013 Avencall
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

from xivo_agent.ami.event import Event
from xivo_agent.ami.response import Response


def parse_msg(data):
    lines = data.split('\r\n')
    first_header, first_value = _parse_line(lines[0])
    if first_header.startswith('Response'):
        msg_factory = Response
    elif first_header.startswith('Event'):
        msg_factory = Event
    else:
        raise Exception('unexpected data: %r' % data)

    headers = {}
    for line in lines[1:]:
        header, value = _parse_line(line)
        headers[header] = value

    return msg_factory(first_value, headers.get('ActionID'), headers)


def _parse_line(line):
    header, value = line.split(':', 1)
    value = value.lstrip()
    return header, value
