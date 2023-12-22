# Copyright 2013-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock

from wazo_agentd.service.action.pause import PauseAction


class TestPauseAction(unittest.TestCase):
    def setUp(self):
        self.amid_client = Mock()
        self.pause_action = PauseAction(self.amid_client)

    def test_pause_agent(self):
        agent_status = Mock()

        reason = 'Want my pause'
        self.pause_action.pause_agent(agent_status, reason)

        self.amid_client.action.assert_called_once_with(
            'QueuePause',
            {
                'Queue': None,
                'Interface': agent_status.interface,
                'Paused': '1',
                'Reason': reason,
            },
        )

    def test_unpause_agent(self):
        agent_status = Mock()

        self.pause_action.unpause_agent(agent_status)

        self.amid_client.action.assert_called_once_with(
            'QueuePause',
            {
                'Queue': None,
                'Interface': agent_status.interface,
                'Paused': '0',
                'Reason': None,
            },
        )
