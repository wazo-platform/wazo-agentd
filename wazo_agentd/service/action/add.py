# Copyright 2013-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, TypeAlias

from wazo_amid_client.exceptions import AmidProtocolError
from xivo_dao.helpers import db_utils

from wazo_agentd.service.helper import format_agent_member_name, format_agent_skills

if TYPE_CHECKING:
    from wazo_amid_client import Client as AmidClient
    from xivo_dao import agent_status_dao as AgentStatusDAO
    from xivo_dao.agent_dao import _Agent as Agent

    from wazo_agentd.dao import _Queue as Queue

    AgentStatus: TypeAlias = AgentStatusDAO._AgentStatus

logger = logging.getLogger(__name__)


class AddToQueueAction:
    def __init__(self, amid_client: AmidClient, agent_status_dao: AgentStatusDAO):
        self._amid_client = amid_client
        self._agent_status_dao = agent_status_dao

    def add_agent_to_queue(self, agent: Agent, queue: Queue):
        with db_utils.session_scope():
            self._agent_status_dao.add_agent_to_queues(agent.id, [queue])
            agent_status = self._agent_status_dao.get_status(agent.id)

        if not agent_status:
            return

        self._update_asterisk(agent_status, queue)

    def add_agent_to_queue_by_status(self, agent_status: AgentStatus, queue: Queue):
        with db_utils.session_scope():
            self._agent_status_dao.add_agent_to_queues(agent_status.agent_id, [queue])

        self._update_asterisk(agent_status, queue)

    def _update_asterisk(self, agent_status: AgentStatus, queue: Queue):
        member_name = format_agent_member_name(agent_status.agent_number)
        skills = format_agent_skills(agent_status.agent_id)
        try:
            self._amid_client.action(
                'QueueAdd',
                {
                    'Queue': queue.name,
                    'Interface': agent_status.interface,
                    'MemberName': member_name,
                    'StateInterface': agent_status.state_interface,
                    'Penalty': queue.penalty,
                    'Skills': skills,
                    **self._format_pause_status(agent_status),
                },
            )
        except AmidProtocolError as e:
            logger.warning(
                'Failure to add interface %s to queue %s: %s',
                agent_status.interface,
                queue.name,
                e,
            )

    def _format_pause_status(self, agent_status: AgentStatus):
        value = {'Paused': '1' if agent_status.paused else '0'}
        if (reason := agent_status.paused_reason) and agent_status.paused:
            value['Reason'] = reason
        return value
