# -*- coding: utf-8 -*-

# Copyright (C) 2012-2014 Avencall
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
