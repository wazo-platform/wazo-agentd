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

logger = logging.getLogger(__name__)


class OnQueueHandler(object):

    def __init__(self, on_queue_added_manager, on_queue_updated_manager, on_queue_deleted_manager, queue_dao):
        self._on_queue_added_manager = on_queue_added_manager
        self._on_queue_updated_manager = on_queue_updated_manager
        self._on_queue_deleted_manager = on_queue_deleted_manager
        self._queue_dao = queue_dao

    @debug.trace_duration
    def handle_on_queue_added(self, queue_id):
        logger.info('Executing on queue added command (ID %s)', queue_id)
        queue = self._queue_dao.get_queue(queue_id)
        self._on_queue_added_manager.on_queue_added(queue)

    @debug.trace_duration
    def handle_on_queue_updated(self, queue_id):
        logger.info('Executing on queue updated command (ID %s)', queue_id)
        queue = self._queue_dao.get_queue(queue_id)
        self._on_queue_updated_manager.on_queue_updated(queue)

    @debug.trace_duration
    def handle_on_queue_deleted(self, queue_id):
        logger.info('Executing on queue deleted command (ID %s)', queue_id)
        self._on_queue_deleted_manager.on_queue_deleted(queue_id)
