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


class OnAgentHandler(object):

    def __init__(self, on_agent_deleted_manager, on_agent_updated_manager, agent_dao):
        self._on_agent_deleted_manager = on_agent_deleted_manager
        self._on_agent_updated_manager = on_agent_updated_manager
        self._agent_dao = agent_dao

    def register_commands(self, agent_server):
        agent_server.add_command(commands.OnAgentUpdatedCommand, self.handle_on_agent_updated)
        agent_server.add_command(commands.OnAgentDeletedCommand, self.handle_on_agent_deleted)

    @debug.trace_duration
    def handle_on_agent_updated(self, command):
        logger.info('Executing on agent updated command (ID %s)', command.agent_id)
        agent = self._agent_dao.get_agent(command.agent_id)
        self._on_agent_updated_manager.on_agent_updated(agent)

    @debug.trace_duration
    def handle_on_agent_deleted(self, command):
        logger.info('Executing on agent deleted command (ID %s)', command.agent_id)
        self._on_agent_deleted_manager.on_agent_deleted(command.agent_id)
