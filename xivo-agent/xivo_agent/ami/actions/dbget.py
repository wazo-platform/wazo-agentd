# -*- coding: UTF-8 -*-

# Copyright (C) 2012-2013  Avencall
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

from xivo_agent.ami.actions.common.action import BaseAction


class DBGetAction(BaseAction):

    def __init__(self, family, key):
        BaseAction.__init__(self, 'DBGet', [
            ('Family', family),
            ('Key', key),
        ])
        self._val = None

    @property
    def val(self):
        self.wait_for_completion()
        return self._val

    def _on_response_received(self, response):
        if not response.is_success():
            self._completed = True

    def _on_event_received(self, event):
        if event.name == 'DBGetComplete':
            self._completed = True
        elif event.name == 'DBGetResponse':
            self._val = event.get_value('Val')
            self._completed = True
        else:
            raise Exception('unexpected event %r' % event)
