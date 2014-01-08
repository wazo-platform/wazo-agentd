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

import logging
from xivo_agent.service.helper import format_agent_member_name, format_agent_skills

logger = logging.getLogger(__name__)


class AddToQueueAction(object):

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
        self._agent_status_dao.add_agent_to_queues(agent_status.agent_id, [queue])
