# -*- coding: utf-8 -*-

# Copyright (C) 2012-2013 Avencall
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

logger = logging.getLogger(__name__)


class LogoffAllAgentsStep(object):

    def __init__(self, remove_agents_from_queues_step, update_queue_log_step, update_agent_status_step, send_agent_logoff_step):
        self._remove_agents_from_queues_step = remove_agents_from_queues_step
        self._update_queue_log_step = update_queue_log_step
        self._update_agent_status_step = update_agent_status_step
        self._send_agent_logoff_step = send_agent_logoff_step

    def execute(self, command, response, blackboard):
        for agent, status in blackboard.logged_in_agents:
            logger.info("logging off agent %s", agent)
            self._remove_agents_from_queues_step.remove_agent_from_queues(status)
            self._update_queue_log_step.log_off_agent(status)
            self._update_agent_status_step.log_off_agent(agent.id)
            self._send_agent_logoff_step.send_agent_logoff(status.agent_id, status.agent_number)
