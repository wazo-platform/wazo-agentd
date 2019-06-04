# Copyright 2012-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


class Event:

    msg_type = 'event'

    def __init__(self, name, action_id, headers):
        self.name = name
        self.action_id = action_id
        self._headers = headers

    def get_value(self, header_name):
        return self._headers[header_name]

    def __repr__(self):
        return '<Event %r>' % self.name
