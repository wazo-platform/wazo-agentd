# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers import db_utils


class OnAgentDeletedManager(object):

    def __init__(self, logoff_action, agent_status_dao):
        self._logoff_action = logoff_action
        self._agent_status_dao = agent_status_dao

    def on_agent_deleted(self, agent_id):
        with db_utils.session_scope():
            agent_status = self._agent_status_dao.get_status(agent_id)
        if agent_status is None:
            return

        self._logoff_action.logoff_agent(agent_status)
