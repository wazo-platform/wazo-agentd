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

import datetime


class LogoffAction(object):

    def __init__(self, ami_client, queue_log_manager, agent_status_dao):
        self._ami_client = ami_client
        self._queue_log_manager = queue_log_manager
        self._agent_status_dao = agent_status_dao

    def logoff_agent(self, agent_status):
        # Precondition:
        # * agent is logged
        self._update_asterisk(agent_status)
        self._update_queue_log(agent_status)
        self._update_agent_status(agent_status)
        self._update_xivo_ctid(agent_status)

    def _update_xivo_ctid(self, agent_status):
        self._ami_client.agent_logoff(agent_status.agent_id, agent_status.agent_number)

    def _update_asterisk(self, agent_status):
        for queue in agent_status.queues:
            self._ami_client.queue_remove(queue.name, agent_status.interface)

    def _update_queue_log(self, agent_status):
        login_time = self._compute_login_time(agent_status.login_at)
        self._queue_log_manager.on_agent_logged_off(agent_status.agent_number, agent_status.extension, agent_status.context, login_time)

    def _compute_login_time(self, login_at):
        delta = datetime.datetime.now() - login_at
        return delta.total_seconds()

    def _update_agent_status(self, agent_status):
        self._agent_status_dao.remove_agent_from_all_queues(agent_status.agent_id)
        self._agent_status_dao.log_off_agent(agent_status.agent_id)
