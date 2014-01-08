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

from collections import namedtuple
from xivo_agent.exception import NoSuchAgentError, NoSuchQueueError

_Queue = namedtuple('_Queue', ['id', 'name', 'penalty'])


class _AbstractDAOAdapter(object):

    def __init__(self, dao):
        self._dao = dao

    def __getattr__(self, name):
        return getattr(self._dao, name)


class AgentDAOAdapter(_AbstractDAOAdapter):

    def get_agent(self, agent_id):
        try:
            return self._dao.agent_with_id(agent_id)
        except LookupError:
            raise NoSuchAgentError()

    def get_agent_by_number(self, agent_number):
        try:
            return self._dao.agent_with_number(agent_number)
        except LookupError:
            raise NoSuchAgentError()


class QueueDAOAdapter(_AbstractDAOAdapter):

    _PENALTY = 0

    def get_queue(self, queue_id):
        try:
            queue_name = self._dao.queue_name(queue_id)
            return _Queue(queue_id, queue_name, self._PENALTY)
        except LookupError:
            raise NoSuchQueueError()
