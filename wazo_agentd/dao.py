# Copyright 2013-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from collections import namedtuple
from wazo_agentd.exception import NoSuchAgentError, NoSuchQueueError

_Queue = namedtuple('_Queue', ['id', 'tenant_uuid', 'name', 'penalty'])


class _AbstractDAOAdapter:
    def __init__(self, dao):
        self._dao = dao

    def __getattr__(self, name):
        return getattr(self._dao, name)


class AgentDAOAdapter(_AbstractDAOAdapter):
    def get_agent(self, agent_id, tenant_uuids=None):
        try:
            return self._dao.agent_with_id(agent_id, tenant_uuids=tenant_uuids)
        except LookupError:
            raise NoSuchAgentError()

    def get_agent_by_number(self, agent_number, tenant_uuids=None):
        try:
            return self._dao.agent_with_number(agent_number, tenant_uuids=tenant_uuids)
        except LookupError:
            raise NoSuchAgentError()


class QueueDAOAdapter(_AbstractDAOAdapter):

    _PENALTY = 0

    def get_queue(self, queue_id, tenant_uuids=None):
        try:
            queue = self._dao.get(queue_id, tenant_uuids=tenant_uuids)
            return _Queue(queue.id, queue.tenant_uuid, queue.name, self._PENALTY)
        except LookupError:
            raise NoSuchQueueError()
