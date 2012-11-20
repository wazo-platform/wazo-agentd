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


class LoginCommand(object):

    name = 'login'

    def __init__(self, agent_number, interface):
        self.agent_number = int(agent_number)
        self.interface = unicode(interface)

    def marshal(self):
        return {
            'number': self.agent_number,
            'interface': self.interface,
        }

    @classmethod
    def unmarshal(cls, msg):
        return cls(msg['number'], msg['interface'])


class LogoffCommand(object):

    name = 'logoff'

    def __init__(self, agent_number):
        self.agent_number = int(agent_number)

    def marshal(self):
        return {
            'number': self.agent_number,
        }

    @classmethod
    def unmarshal(cls, msg):
        return cls(msg['number'])


class StatusCommand(object):

    name = 'status'

    def __init__(self, agent_number):
        self.agent_number = int(agent_number)

    def marshal(self):
        return {
            'number': self.agent_number
        }

    @classmethod
    def unmarshal(cls, msg):
        return cls(msg['number'])
