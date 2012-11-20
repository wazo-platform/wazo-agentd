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

    def __init__(self, agent_id, interface):
        self.agent_id = int(agent_id)
        self.interface = unicode(interface)

    def marshal(self):
        return {
            'id': self.agent_id,
            'interface': self.interface,
        }

    @classmethod
    def unmarshal(cls, msg):
        return cls(msg['id'], msg['interface'])


class LogoffCommand(object):

    name = 'logoff'

    def __init__(self, agent_id):
        self.agent_id = int(agent_id)

    def marshal(self):
        return {
            'id': self.agent_id,
        }

    @classmethod
    def unmarshal(cls, msg):
        return cls(msg['id'])


class StatusCommand(object):

    name = 'status'

    def __init__(self, agent_id):
        self.agent_id = int(agent_id)

    def marshal(self):
        return {
            'id': self.agent_id,
        }

    @classmethod
    def unmarshal(cls, msg):
        return cls(msg['id'])
