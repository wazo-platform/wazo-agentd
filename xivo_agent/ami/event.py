# -*- coding: utf-8 -*-
# Copyright (C) 2012-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+


class Event(object):

    msg_type = 'event'

    def __init__(self, name, action_id, headers):
        self.name = name
        self.action_id = action_id
        self._headers = headers

    def get_value(self, header_name):
        return self._headers[header_name]

    def __repr__(self):
        return '<Event %r>' % self.name
