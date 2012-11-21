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

    def __init__(self, agent_id, extension, context):
        self.agent_id = int(agent_id)
        self.extension = unicode(extension)
        self.context = unicode(context)

    def marshal(self):
        return {
            'id': self.agent_id,
            'extension': self.extension,
            'context': self.context,
        }

    @classmethod
    def unmarshal(cls, msg):
        return cls(msg['id'], msg['extension'], msg['context'])


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
