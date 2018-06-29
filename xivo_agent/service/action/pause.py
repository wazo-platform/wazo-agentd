# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+


class PauseAction(object):

    def __init__(self, ami_client):
        self._ami_client = ami_client

    def pause_agent(self, agent_status, reason):
        self._ami_client.queue_pause(agent_status.interface, '1', reason)

    def unpause_agent(self, agent_status):
        self._ami_client.queue_pause(agent_status.interface, '0')
