# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import datetime
import unittest
from functools import wraps
from mock import ANY, Mock, patch, sentinel
from xivo_agent.queuelog import QueueLogManager

mock_date = datetime.datetime(2011, 11, 12, 13, 14, 15, 1617)
mock_date_str = '2011-11-12 13:14:15.001617'


class patch_datetime_now(object):
    def __init__(self, *mock_args, **mock_kwargs):
        self.mock_args = mock_args
        self.mock_kwargs = mock_kwargs

    def __call__(self, wrapped):
        @wraps(wrapped)
        def wrapper(*args, **kwargs):
            with patch('datetime.datetime') as datetime_mock:
                datetime_mock.now = Mock(*self.mock_args, **self.mock_kwargs)
                wrapped(*args, **kwargs)
        return wrapper


class TestQueuelog(unittest.TestCase):

    def setUp(self):
        self.queue_log_dao = Mock()
        self.queue_log_mgr = QueueLogManager(self.queue_log_dao)

    def test_format_time(self):
        dt = mock_date
        expected = mock_date_str

        value = QueueLogManager.format_time(dt)

        self.assertEqual(expected, value)

    @patch_datetime_now(return_value=mock_date)
    def test_format_time_now(self):
        expected = mock_date_str

        value = QueueLogManager.format_time_now()

        self.assertEqual(expected, value)

    @patch_datetime_now(return_value=mock_date)
    def test_on_agent_logged_in(self):
        str_now = mock_date_str

        self.queue_log_mgr.on_agent_logged_in('1', '1001', 'default')

        self.queue_log_dao.insert_entry.assert_called_once_with(
            str_now,
            'NONE',
            'NONE',
            'Agent/1',
            'AGENTCALLBACKLOGIN',
            '1001@default',
        )

    @patch_datetime_now(return_value=mock_date)
    def test_on_agent_logged_off(self):
        str_now = mock_date_str

        self.queue_log_mgr.on_agent_logged_off('1', '1001', 'default', 123)

        self.queue_log_dao.insert_entry.assert_called_once_with(
            str_now,
            'NONE',
            'NONE',
            'Agent/1',
            'AGENTCALLBACKLOGOFF',
            '1001@default',
            '123',
            'CommandLogoff',
        )

    def test_on_agent_logged_off_written_logged_time_should_be_an_integer_when_given_logged_time_is_not_integer(self):
        self.queue_log_mgr.on_agent_logged_off(sentinel.agent_number,
                                               sentinel.extension,
                                               sentinel.context,
                                               12.98743)

        self.queue_log_dao.insert_entry.assert_called_once_with(ANY, ANY, ANY, ANY, ANY, ANY, '12', ANY)
