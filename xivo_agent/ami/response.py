# Copyright 2012-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


class Response:

    msg_type = 'response'

    def __init__(self, response, action_id, headers):
        self.response = response
        self.action_id = action_id
        self._headers = headers

    def is_success(self):
        return self.response == 'Success'

    def __repr__(self):
        return '<Response %r>' % self.response
