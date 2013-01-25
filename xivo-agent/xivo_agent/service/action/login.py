# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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
from xivo_agent.exception import NoSuchExtensionError
from xivo_agent.service.helper import format_agent_member_name,\
    format_agent_skills

logger = logging.getLogger(__name__)


class LoginAction(object):

    def __init__(self, ami_client, queue_log_manager, agent_status_dao, line_dao):
        self._ami_client = ami_client
        self._queue_log_manager = queue_log_manager
        self._agent_status_dao = agent_status_dao
        self._line_dao = line_dao

    def login_agent(self, agent, extension, context):
        # Precondition:
        # * agent is not logged
        # * extension@context is not used
        interface = self._get_interface(agent)
        state_interface = self._get_state_interface(extension, context)
        self._update_agent_status(agent, extension, context, interface, state_interface)
        self._update_queue_log(agent, extension, context)
        self._update_asterisk(agent, interface, state_interface)
        self._update_xivo_ctid(agent, extension, context)

    def _get_interface(self, agent):
        return 'Local/id-{0}@agentcallback'.format(agent.id)

    def _get_state_interface(self, extension, context):
        try:
            return self._line_dao.get_interface_from_exten_and_context(extension, context)
        except LookupError:
            raise NoSuchExtensionError(extension, context)

    def _update_agent_status(self, agent, extension, context, interface, state_interface):
        self._agent_status_dao.log_in_agent(agent.id, agent.number, extension, context, interface, state_interface)
        self._agent_status_dao.add_agent_to_queues(agent.id, agent.queues)

    def _update_queue_log(self, agent, extension, context):
        self._queue_log_manager.on_agent_logged_in(agent.number, extension, context)

    def _update_asterisk(self, agent, interface, state_interface):
        member_name = format_agent_member_name(agent.number)
        skills = format_agent_skills(agent.number)
        for queue in agent.queues:
            action = self._ami_client.queue_add(queue.name, interface, member_name, state_interface,
                                                queue.penalty, skills)
            if not action.success:
                logger.warning('Failure to add interface %r to queue %r', interface, queue.name)

    def _update_xivo_ctid(self, agent, extension, context):
        self._ami_client.agent_login(agent.id, agent.number, extension, context)
