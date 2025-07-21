# Copyright 2013-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from xivo_dao.helpers import db_utils

logger = logging.getLogger(__name__)


class OnAgentDeletedManager:
    def __init__(self, logoff_action, agent_status_dao):
        self._logoff_action = logoff_action
        self._agent_status_dao = agent_status_dao

    def on_agent_deleted(self, agent_id):
        with db_utils.session_scope():
            agent_status = (
                self._agent_status_dao.get_agent_login_status_by_id_for_logoff(agent_id)
            )
        if agent_status is None:
            logger.debug('agent %d has no active status requiring logoff', agent_id)
            return

        self._logoff_action.logoff_agent(agent_status)
