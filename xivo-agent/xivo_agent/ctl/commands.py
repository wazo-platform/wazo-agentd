# -*- coding: UTF-8 -*-


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
