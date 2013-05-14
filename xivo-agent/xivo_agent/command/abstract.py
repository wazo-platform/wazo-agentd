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

from __future__ import unicode_literals


class AbstractNoDataCommand(object):

    def __init__(self):
        pass

    def marshal(self):
        return None

    @classmethod
    def unmarshal(cls, msg):
        return cls()


class AbstractAgentIDCommand(object):

    def __init__(self, agent_id):
        self.agent_id = int(agent_id)

    def marshal(self):
        return {'agent_id': self.agent_id}

    @classmethod
    def unmarshal(cls, msg):
        return cls(msg['agent_id'])


class AbstractAgentNumberCommand(object):

    def __init__(self, agent_number):
        self.agent_number = unicode(agent_number)

    def marshal(self):
        return {'agent_number': self.agent_number}

    @classmethod
    def unmarshal(cls, msg):
        return cls(msg['agent_number'])


class AbstractQueueIDCommand(object):

    def __init__(self, queue_id):
        self.queue_id = int(queue_id)

    def marshal(self):
        return {'queue_id': self.queue_id}

    @classmethod
    def unmarshal(cls, msg):
        return cls(msg['queue_id'])


class AbstractAgentAndQueueIDCommand(object):

    def __init__(self, agent_id, queue_id):
        self.agent_id = int(agent_id)
        self.queue_id = int(queue_id)

    def marshal(self):
        return {'agent_id': self.agent_id, 'queue_id': self.queue_id}

    @classmethod
    def unmarshal(cls, msg):
        return cls(msg['agent_id'], msg['queue_id'])
