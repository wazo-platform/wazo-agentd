# Copyright 2013-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


class PauseAction:

    def __init__(self, ami_client):
        self._ami_client = ami_client

    def pause_agent(self, agent_status, reason):
        self._ami_client.queue_pause(agent_status.interface, '1', reason)

    def unpause_agent(self, agent_status):
        self._ami_client.queue_pause(agent_status.interface, '0')
