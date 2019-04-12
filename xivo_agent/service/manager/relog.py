# Copyright 2013-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from xivo_dao.helpers import db_utils

logger = logging.getLogger(__name__)


class RelogManager:

    def __init__(self, login_action, logoff_action, agent_dao, agent_status_dao):
        self._login_action = login_action
        self._logoff_action = logoff_action
        self._agent_dao = agent_dao
        self._agent_status_dao = agent_status_dao

    def relog_all_agents(self, tenant_uuids=None):
        agent_statuses = self._get_agent_statuses(tenant_uuids=tenant_uuids)
        for agent_status in agent_statuses:
            try:
                self._relog_agent(agent_status)
            except Exception:
                logger.warning('Could not relog agent %s', agent_status.agent_id, exc_info=True)

    def _get_agent_statuses(self, tenant_uuids=None):
        with db_utils.session_scope():
            agent_ids = self._agent_status_dao.get_logged_agent_ids(tenant_uuids=tenant_uuids)
            return [self._agent_status_dao.get_status(agent_id) for agent_id in agent_ids]

    def _relog_agent(self, agent_status):
        self._logoff_action.logoff_agent(agent_status)
        with db_utils.session_scope():
            agent = self._agent_dao.get_agent(agent_status.agent_id)
        self._login_action.login_agent(agent, agent_status.extension, agent_status.context)
