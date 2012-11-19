# -*- coding: UTF-8 -*-


class CommandResponse(object):

    ERR_SERVER = 'server error'
    ERR_CLIENT = 'client error'

    def __init__(self, error=None, value=None):
        self.error = error
        self.value = value

    def marshal(self):
        return {
            'error': self.error,
            'value': self.value,
        }

    @classmethod
    def unmarshal(cls, msg):
        return cls(msg['error'], msg['value'])
