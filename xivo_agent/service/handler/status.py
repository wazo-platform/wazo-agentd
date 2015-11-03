# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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

from xivo import debug
from xivo_dao.helpers import db_utils

logger = logging.getLogger(__name__)


class StatusHandler(object):

    def __init__(self, agent_dao, agent_status_dao, uuid):
        self._agent_dao = agent_dao
        self._agent_status_dao = agent_status_dao
        self._uuid = uuid

    @debug.trace_duration
    def handle_status_by_id(self, agent_id):
        logger.info('Executing status command (ID %s)', agent_id)
        with db_utils.session_scope():
            agent = self._agent_dao.get_agent(agent_id)
        return self._handle_status(agent)

    @debug.trace_duration
    def handle_status_by_number(self, agent_number):
        logger.info('Executing status command (number %s)', agent_number)
        with db_utils.session_scope():
            agent = self._agent_dao.get_agent_by_number(agent_number)
        return self._handle_status(agent)

    @debug.trace_duration
    def handle_statuses(self,):
        logger.info('Executing statuses command')
        with db_utils.session_scope():
            agent_statuses = self._agent_status_dao.get_statuses()
            return [
                {'id': status.agent_id,
                 'origin_uuid': self._uuid,
                 'number': status.agent_number,
                 'logged': status.logged,
                 'extension': status.extension,
                 'context': status.context,
                 'state_interface': status.state_interface}
                for status in agent_statuses
            ]

    def _handle_status(self, agent):
        with db_utils.session_scope():
            agent_status = self._agent_status_dao.get_status(agent.id)
            if agent_status is None:
                logged = False
                extension = None
                context = None
                state_interface = None
            else:
                logged = True
                extension = agent_status.extension
                context = agent_status.context
                state_interface = agent_status.state_interface
            return {
                'id': agent.id,
                'origin_uuid': self._uuid,
                'number': agent.number,
                'logged': logged,
                'extension': extension,
                'context': context,
                'state_interface': state_interface,
            }
