# Copyright 2013-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from collections import namedtuple
from xivo_agent.exception import NoSuchAgentError, NoSuchQueueError

_Queue = namedtuple('_Queue', ['id', 'name', 'penalty'])


class _AbstractDAOAdapter:

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
