# Copyright 2013-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_agentd.exception import AgentNotLoggedError


class PauseManager:
    def __init__(self, pause_action):
        self._pause_action = pause_action

    def pause_agent(self, agent_status, reason):
        self._check_agent_status(agent_status)
        self._pause_action.pause_agent(agent_status, reason)

    def unpause_agent(self, agent_status):
        self._check_agent_status(agent_status)
        self._pause_action.unpause_agent(agent_status)

    def _check_agent_status(self, agent_status):
        if agent_status is None:
            raise AgentNotLoggedError()
