# -*- coding: UTF-8 -*-

# Copyright (C) 2012-2013  Avencall
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

from collections import namedtuple
from xivo_agent.ctl import error

_Queue = namedtuple('_Queue', ['id', 'name'])


class GetQueueStep(object):

    def __init__(self, queue_dao):
        self._queue_dao = queue_dao

    def execute(self, command, response, blackboard):
        try:

            blackboard.queue = self.get_queue(command.queue_id)
        except LookupError:
            response.error = error.NO_SUCH_QUEUE

    def get_queue(self, queue_id):
        queue_name = self._queue_dao.queue_name(queue_id)
        return _Queue(queue_id, queue_name)
