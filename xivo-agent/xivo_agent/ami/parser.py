# -*- coding: UTF-8 -*-

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
