# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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
from xivo_bus.ressource.agent import command as commands

logger = logging.getLogger(__name__)


class StatusHandler(object):

    def __init__(self, agent_dao, agent_status_dao):
        self._agent_dao = agent_dao
        self._agent_status_dao = agent_status_dao

    def register_commands(self, agent_server):
        agent_server.add_command(commands.StatusByIDCommand, self.handle_status_by_id)
        agent_server.add_command(commands.StatusByNumberCommand, self.handle_status_by_number)
        agent_server.add_command(commands.StatusesCommand, self.handle_statuses)

    @debug.trace_duration
    def handle_status_by_id(self, command):
        logger.info('Executing status command (ID %s)', command.agent_id)
        agent = self._agent_dao.get_agent(command.agent_id)
        return self._handle_status(agent)

    @debug.trace_duration
    def handle_status_by_number(self, command):
        logger.info('Executing status command (number %s)', command.agent_number)
        agent = self._agent_dao.get_agent_by_number(command.agent_number)
        return self._handle_status(agent)

    @debug.trace_duration
    def handle_statuses(self, command):
        logger.info('Executing statuses command')
        agent_statuses = self._agent_status_dao.get_statuses()
        return [
            {'id': status.agent_id,
             'number': status.agent_number,
             'logged': status.logged,
             'extension': status.extension,
             'context': status.context}
            for status in agent_statuses
        ]

    def _handle_status(self, agent):
        agent_status = self._agent_status_dao.get_status(agent.id)
        if agent_status is None:
            logged = False
            extension = None
            context = None
        else:
            logged = True
            extension = agent_status.extension
            context = agent_status.context
        return {
            'id': agent.id,
            'number': agent.number,
            'logged': logged,
            'extension': extension,
            'context': context,
        }
