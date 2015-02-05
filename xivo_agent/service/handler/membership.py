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
from xivo_agent.resources.agent import command as commands

logger = logging.getLogger(__name__)


class MembershipHandler(object):

    def __init__(self, add_member_manager, remove_member_manager, agent_dao, queue_dao):
        self._add_member_manager = add_member_manager
        self._remove_member_manager = remove_member_manager
        self._agent_dao = agent_dao
        self._queue_dao = queue_dao

    def register_commands(self, agent_server):
        agent_server.add_command(commands.AddToQueueCommand, self.handle_add_to_queue)
        agent_server.add_command(commands.RemoveFromQueueCommand, self.handle_remove_from_queue)

    @debug.trace_duration
    def handle_add_to_queue(self, command):
        logger.info('Executing add to queue command (agent ID %s, queue ID %s)', command.agent_id, command.queue_id)
        agent = self._agent_dao.get_agent(command.agent_id)
        queue = self._queue_dao.get_queue(command.queue_id)
        self._add_member_manager.add_agent_to_queue(agent, queue)

    @debug.trace_duration
    def handle_remove_from_queue(self, command):
        logger.info('Executing remove from queue command (agent ID %s, queue ID %s)', command.agent_id, command.queue_id)
        agent = self._agent_dao.get_agent(command.agent_id)
        queue = self._queue_dao.get_queue(command.queue_id)
        self._remove_member_manager.remove_agent_from_queue(agent, queue)
