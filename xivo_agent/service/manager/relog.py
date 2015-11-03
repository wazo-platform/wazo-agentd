# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import logging

from xivo_dao.helpers import db_utils

logger = logging.getLogger(__name__)


class RelogManager(object):

    def __init__(self, login_action, logoff_action, agent_dao, agent_status_dao):
        self._login_action = login_action
        self._logoff_action = logoff_action
        self._agent_dao = agent_dao
        self._agent_status_dao = agent_status_dao

    def relog_all_agents(self):
        agent_statuses = self._get_agent_statuses()
        for agent_status in agent_statuses:
            try:
                self._relog_agent(agent_status)
            except Exception:
                logger.warning('Could not relog agent %s', agent_status.agent_id, exc_info=True)

    def _get_agent_statuses(self):
        with db_utils.session_scope():
            agent_ids = self._agent_status_dao.get_logged_agent_ids()
            return [self._agent_status_dao.get_status(agent_id) for agent_id in agent_ids]

    def _relog_agent(self, agent_status):
        self._logoff_action.logoff_agent(agent_status)
        with db_utils.session_scope():
            agent = self._agent_dao.get_agent(agent_status.agent_id)
        self._login_action.login_agent(agent, agent_status.extension, agent_status.context)
