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


class BaseAction(object):

    def __init__(self, name, headers):
        self._name = name
        self._lines = self._format_headers(headers)
        # package private attributes
        self._action_id = None
        self._amiclient = None
        self._completed = False
        self._response = None

    def _format_headers(self, headers):
        return ['%s: %s' % (header, value) for (header, value) in headers if
                value is not None]

    def format(self):
        lines = ['Action: %s' % self._name]
        if self._action_id is not None:
            lines.append('ActionID: %s' % self._action_id)
        lines.extend(self._lines)
        lines.append('\r\n')
        return '\r\n'.join(lines).encode('UTF-8')

    @property
    def success(self):
        self.wait_for_completion()
        return self._response.is_success()

    def wait_for_completion(self):
        if not self._completed:
            self._amiclient.wait_for_completion(self)

    # package private method
    def _on_response_received(self, response):
        # may be overridden
        self._completed = True

    # package private method
    def _on_event_received(self, event):
        # may be overridden
        pass
