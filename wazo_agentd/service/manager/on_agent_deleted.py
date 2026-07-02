# Copyright 2013-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from xivo_dao.helpers import db_utils

logger = logging.getLogger(__name__)


class OnAgentDeletedManager:
    def __init__(self, logoff_action, agent_status_dao):
        self._logoff_action = logoff_action
        self._agent_status_dao = agent_status_dao

    def on_agent_deleted(self, agent_id, tenant_uuid):
        with db_utils.session_scope():
            agent_status = (
                self._agent_status_dao.get_agent_login_status_by_id_for_logoff(agent_id)
            )
        if agent_status is None:
            logger.debug('agent %d has no active status requiring logoff', agent_id)
        else:
            # The agent row is already deleted, so the status can only carry
            # the tenant_uuid taken from the agent_deleted event
            agent_status = agent_status._replace(tenant_uuid=tenant_uuid)
            self._logoff_action.logoff_agent(agent_status)

        with db_utils.session_scope():
            self._agent_status_dao.remove_agent_from_all_queues(agent_id)
