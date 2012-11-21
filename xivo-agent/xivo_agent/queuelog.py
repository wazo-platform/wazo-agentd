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

import datetime


class QueueLogManager(object):

    def __init__(self, queue_log_dao):
        self._dao = queue_log_dao

    def on_agent_logged_in(self, agent_number, extension, context):
        time = self.format_time_now()
        agent = self._format_agent(agent_number)
        data1 = self._format_data1(extension, context)

        self._dao.insert_entry(time, 'NONE', 'NONE', agent, 'AGENTCALLBACKLOGIN',
                               data1)

    def on_agent_logged_off(self, agent_number, extension, context, logged_time):
        time = self.format_time_now()
        agent = self._format_agent(agent_number)
        data1 = self._format_data1(extension, context)

        self._dao.insert_entry(time, 'NONE', 'NONE', agent, 'AGENTCALLBACKLOGOFF',
                               data1, str(logged_time), 'CommandLogoff')

    def _format_agent(self, agent_number):
        return 'Agent/%s' % agent_number

    def _format_data1(self, extension, context):
        return '%s@%s' % (extension, context)

    @classmethod
    def format_time(cls, dt):
        return dt.strftime('%Y-%m-%d %H:%M:%S.%f')

    @classmethod
    def format_time_now(cls):
        return cls.format_time(datetime.datetime.now())
