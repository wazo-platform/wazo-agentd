# -*- coding: UTF-8 -*-


class Response(object):

    msg_type = 'response'

    def __init__(self, response, action_id, headers):
        self.response = response
        self.action_id = action_id
        self._headers = headers

    def is_success(self):
        return self.response == 'Success'

    def __repr__(self):
        return '<Response %r>' % self.response
