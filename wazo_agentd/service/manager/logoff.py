# Copyright 2013-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_agentd.exception import AgentNotLoggedError
from xivo_dao.helpers import db_utils


class LogoffManager:
    def __init__(self, logoff_action, agent_status_dao):
        self._logoff_action = logoff_action
        self._agent_status_dao = agent_status_dao

    def logoff_agent(self, agent_status):
        if agent_status is None:
            raise AgentNotLoggedError()
        self._logoff_action.logoff_agent(agent_status)

    def logoff_all_agents(self, tenant_uuids=None):
        agent_statuses = self._get_agent_statuses(tenant_uuids=tenant_uuids)
        for agent_status in agent_statuses:
            self._logoff_action.logoff_agent(agent_status)

    def _get_agent_statuses(self, tenant_uuids=None):
        with db_utils.session_scope():
            agent_ids = self._agent_status_dao.get_logged_agent_ids(
                tenant_uuids=tenant_uuids
            )
            return [
                self._agent_status_dao.get_status(agent_id) for agent_id in agent_ids
            ]
