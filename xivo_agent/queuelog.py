# Copyright 2012-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import datetime
from xivo_dao.helpers import db_utils


class QueueLogManager:

    def __init__(self, queue_log_dao):
        self._dao = queue_log_dao

    def on_agent_logged_in(self, agent_number, extension, context):
        time = self.format_time_now()
        agent = self._format_agent(agent_number)
        data1 = self._format_data1(extension, context)

        with db_utils.session_scope():
            self._dao.insert_entry(time, 'NONE', 'NONE', agent, 'AGENTCALLBACKLOGIN',
                                   data1)

    def on_agent_logged_off(self, agent_number, extension, context, logged_time):
        time = self.format_time_now()
        agent = self._format_agent(agent_number)
        data1 = self._format_data1(extension, context)
        logged_time = self._format_logged_time(logged_time)

        with db_utils.session_scope():
            self._dao.insert_entry(time, 'NONE', 'NONE', agent, 'AGENTCALLBACKLOGOFF',
                                   data1, logged_time, 'CommandLogoff')

    def _format_agent(self, agent_number):
        return 'Agent/%s' % agent_number

    def _format_data1(self, extension, context):
        return '%s@%s' % (extension, context)

    def _format_logged_time(self, logged_time):
        return str(int(logged_time))

    @classmethod
    def format_time(cls, dt):
        return dt.strftime('%Y-%m-%d %H:%M:%S.%f')

    @classmethod
    def format_time_now(cls):
        return cls.format_time(datetime.datetime.now())
