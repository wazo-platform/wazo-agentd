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


class _AbstractAgentCommand(object):

    def __init__(self):
        self.agent_id = None
        self.agent_number = None

    def by_id(self, agent_id):
        self.agent_id = int(agent_id)
        return self

    def by_number(self, agent_number):
        self.agent_number = unicode(agent_number)
        return self

    def _set_agent_id_and_number(self, agent_id, agent_number):
        if agent_id is not None:
            self.agent_id = int(agent_id)
        if agent_number is not None:
            self.agent_number = unicode(agent_number)


class AddToQueueCommand(object):

    name = 'add_to_queue'

    def __init__(self, agent_id, queue_id):
        self.agent_id = int(agent_id)
        self.queue_id = int(queue_id)

    def marshal(self):
        return {
            'agent_id': self.agent_id,
            'queue_id': self.queue_id,
        }

    @classmethod
    def unmarshal(cls, msg):
        return cls(msg['agent_id'], msg['queue_id'])


class LoginCommand(_AbstractAgentCommand):

    name = 'login'

    def __init__(self, extension, context):
        _AbstractAgentCommand.__init__(self)
        self.extension = unicode(extension)
        self.context = unicode(context)

    def marshal(self):
        return {
            'agent_id': self.agent_id,
            'agent_number': self.agent_number,
            'extension': self.extension,
            'context': self.context,
        }

    @classmethod
    def unmarshal(cls, msg):
        cmd = cls(msg['extension'], msg['context'])
        cmd._set_agent_id_and_number(msg['agent_id'], msg['agent_number'])
        return cmd


class LogoffCommand(_AbstractAgentCommand):

    name = 'logoff'

    def marshal(self):
        return {
            'agent_id': self.agent_id,
            'agent_number': self.agent_number,
        }

    @classmethod
    def unmarshal(cls, msg):
        cmd = cls()
        cmd._set_agent_id_and_number(msg['agent_id'], msg['agent_number'])
        return cmd


class StatusCommand(_AbstractAgentCommand):

    name = 'status'

    def marshal(self):
        return {
            'agent_id': self.agent_id,
            'agent_number': self.agent_number,
        }

    @classmethod
    def unmarshal(cls, msg):
        cmd = cls()
        cmd._set_agent_id_and_number(msg['agent_id'], msg['agent_number'])
        return cmd


class StatusesCommand(object):

    name = 'statuses'

    def marshal(self):
        return None

    @classmethod
    def unmarshal(cls, msg):
        return cls()


class PingCommand(object):

    name = 'ping'

    def marshal(self):
        return None

    @classmethod
    def unmarshal(cls, msg):
        return cls()
