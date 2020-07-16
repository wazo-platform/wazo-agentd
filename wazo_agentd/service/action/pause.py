# Copyright 2013-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


class PauseAction:
    def __init__(self, amid_client):
        self._amid_client = amid_client

    def pause_agent(self, agent_status, reason):
        self._amid_client.action(
            'QueuePause',
            {
                'Queue': None,
                'Interface': agent_status.interface,
                'Paused': '1',
                'Reason': reason,
            },
        )

    def unpause_agent(self, agent_status):
        self._amid_client.action(
            'QueuePause',
            {
                'Queue': None,
                'Interface': agent_status.interface,
                'Paused': '0',
                'Reason': None,
            },
        )
