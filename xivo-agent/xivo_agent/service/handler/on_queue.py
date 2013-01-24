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
from xivo_agent import command

logger = logging.getLogger(__name__)


class OnQueueHandler(object):
    # XXX bad name

    def __init__(self, on_queue_added_manager, on_queue_updated_manager, on_queue_deleted_manager, queue_dao):
        self._on_queue_added_manager = on_queue_added_manager
        self._on_queue_updated_manager = on_queue_updated_manager
        self._on_queue_deleted_manager = on_queue_deleted_manager
        self._queue_dao = queue_dao

    def register_commands(self, agent_server):
        agent_server.add_command(command.OnQueueAddedCommand, self.handle_on_queue_added)
        agent_server.add_command(command.OnQueueUpdatedCommand, self.handle_on_queue_updated)
        agent_server.add_command(command.OnQueueDeletedCommand, self.handle_on_queue_deleted)

    @debug.trace_duration
    def handle_on_queue_added(self, command):
        logger.info('Executing on queue added command (ID %s)', command.queue_id)
        queue = self._queue_dao.get_queue(command.queue_id)
        self._on_queue_added_manager.on_queue_added(queue)

    @debug.trace_duration
    def handle_on_queue_updated(self, command):
        logger.info('Executing on queue updated command (ID %s)', command.queue_id)
        queue = self._queue_dao.get_queue(command.queue_id)
        self._on_queue_updated_manager.on_queue_updated(queue)

    @debug.trace_duration
    def handle_on_queue_deleted(self, command):
        logger.info('Executing on queue deleted command (ID %s)', command.queue_id)
        self._on_queue_deleted_manager.on_queue_deleted(command.queue_id)
