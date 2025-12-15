# Copyright 2013-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from wazo_amid_client.exceptions import AmidProtocolError
from xivo_dao.helpers import db_utils

from wazo_agentd.service.helper import format_agent_member_name, format_agent_skills

logger = logging.getLogger(__name__)


class AddToQueueAction:
    def __init__(self, amid_client, agent_status_dao):
        self._amid_client = amid_client
        self._agent_status_dao = agent_status_dao

    def add_agent_to_queue(self, agent_status, queue):
        self._update_asterisk(agent_status, queue)
        self._update_agent_status(agent_status, queue)

    def _update_asterisk(self, agent_status, queue):
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

    def _update_agent_status(self, agent_status, queue):
        with db_utils.session_scope():
            self._agent_status_dao.add_agent_to_queues(agent_status.agent_id, [queue])

    def _format_pause_status(self, agent_status):
        value = {'Paused': '1' if agent_status.paused else '0'}
        if reason := agent_status.paused_reason and agent_status.paused:
            value['Reason'] = reason
        return value
