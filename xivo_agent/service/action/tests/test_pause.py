# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest
from mock import Mock
from xivo_agent.service.action.pause import PauseAction


class TestPauseAction(unittest.TestCase):

    def setUp(self):
        self.ami_client = Mock()
        self.pause_action = PauseAction(self.ami_client)

    def test_pause_agent(self):
        agent_status = Mock()

        reason = 'Want my pause'
        self.pause_action.pause_agent(agent_status, reason)

        self.ami_client.queue_pause.assert_called_once_with(agent_status.interface, '1', reason)

    def test_unpause_agent(self):
        agent_status = Mock()

        self.pause_action.unpause_agent(agent_status)

        self.ami_client.queue_pause.assert_called_once_with(agent_status.interface, '0')
