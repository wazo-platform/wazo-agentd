# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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
import unittest
from mock import Mock, patch
from xivo_agent.queuelog import QueueLogManager


class TestQueuelog(unittest.TestCase):

    def test_format_time(self):
        dt = datetime.datetime(2011, 11, 12, 13, 14, 15, 1617)
        expected = '2011-11-12 13:14:15.001617'

        value = QueueLogManager.format_time(dt)

        self.assertEqual(expected, value)

    def test_format_time_now(self):
        dt_now = datetime.datetime(2011, 11, 12, 13, 14, 15, 1617)
        str_now = '2011-11-12 13:14:15.001617'
        with patch('datetime.datetime') as datetime_mock:
            datetime_mock.now.return_value = dt_now

            value = QueueLogManager.format_time_now()

            self.assertEqual(str_now, value)

    def test_on_agent_logged_in(self):
        dt_now = datetime.datetime(2011, 11, 12, 13, 14, 15, 1617)
        str_now = '2011-11-12 13:14:15.001617'
        with patch('datetime.datetime') as datetime_mock:
            datetime_mock.now.return_value = dt_now
            queue_log_dao = Mock()
            queue_log_mgr = QueueLogManager(queue_log_dao)

            queue_log_mgr.on_agent_logged_in('1', '1001', 'default')

            queue_log_dao.insert_entry.assert_called_once_with(
                str_now,
                'NONE',
                'NONE',
                'Agent/1',
                'AGENTCALLBACKLOGIN',
                '1001@default',
            )

    def test_on_agent_logged_off(self):
        dt_now = datetime.datetime(2011, 11, 12, 13, 14, 15, 1617)
        str_now = '2011-11-12 13:14:15.001617'
        with patch('datetime.datetime') as datetime_mock:
            datetime_mock.now.return_value = dt_now
            queue_log_dao = Mock()
            queue_log_mgr = QueueLogManager(queue_log_dao)

            queue_log_mgr.on_agent_logged_off('1', '1001', 'default', 123)

            queue_log_dao.insert_entry.assert_called_once_with(
                str_now,
                'NONE',
                'NONE',
                'Agent/1',
                'AGENTCALLBACKLOGOFF',
                '1001@default',
                '123',
                'CommandLogoff',
            )
