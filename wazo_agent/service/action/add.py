# Copyright 2013-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from wazo_agent.service.helper import format_agent_member_name, format_agent_skills
from xivo_dao.helpers import db_utils

logger = logging.getLogger(__name__)


class AddToQueueAction:

    def __init__(self, ami_client, agent_status_dao):
        self._ami_client = ami_client
        self._agent_status_dao = agent_status_dao

    def add_agent_to_queue(self, agent_status, queue):
        self._update_asterisk(agent_status, queue)
        self._update_agent_status(agent_status, queue)

    def _update_asterisk(self, agent_status, queue):
        member_name = format_agent_member_name(agent_status.agent_number)
        skills = format_agent_skills(agent_status.agent_id)
        action = self._ami_client.queue_add(queue.name, agent_status.interface, member_name, agent_status.state_interface,
                                            queue.penalty, skills)
        if not action.success:
            logger.warning('Failure to add interface %r to queue %r', agent_status.interface, queue.name)

    def _update_agent_status(self, agent_status, queue):
        with db_utils.session_scope():
            self._agent_status_dao.add_agent_to_queues(agent_status.agent_id, [queue])
