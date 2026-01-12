# Copyright 2013-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, TypeAlias

from wazo_amid_client.exceptions import AmidProtocolError
from xivo_dao.helpers import db_utils

if TYPE_CHECKING:
    from wazo_amid_client import Client as AmidClient
    from xivo_dao import agent_status_dao as AgentStatusDAO
    from xivo_dao.agent_dao import _Agent as Agent

    from wazo_agentd.dao import _Queue as Queue

    AgentStatus: TypeAlias = AgentStatusDAO._AgentStatus

logger = logging.getLogger(__name__)


class RemoveFromQueueAction:
    def __init__(self, amid_client: AmidClient, agent_status_dao: AgentStatusDAO):
        self._amid_client = amid_client
        self._agent_status_dao = agent_status_dao

    def remove_agent_from_queue(self, agent: Agent, queue: Queue):
        with db_utils.session_scope():
            self._agent_status_dao.remove_agent_from_queues(agent.id, [queue.id])
            agent_status = self._agent_status_dao.get_status(agent.id)

        if agent_status:
            self._update_asterisk(agent_status, queue)

    def remove_agent_from_queue_by_status(
        self, agent_status: AgentStatus, queue: Queue
    ):
        with db_utils.session_scope():
            self._agent_status_dao.remove_agent_from_queues(
                agent_status.agent_id, [queue.id]
            )

        self._update_asterisk(agent_status, queue)

    def _update_asterisk(self, agent_status: AgentStatus, queue: Queue):
        try:
            self._amid_client.action(
                'QueueRemove',
                {
                    'Queue': queue.name,
                    'Interface': agent_status.interface,
                },
            )
        except AmidProtocolError as e:
            logger.warning(
                'Failure to remove interface %s from queue %s: %s',
                agent_status.interface,
                queue.name,
                e,
            )
