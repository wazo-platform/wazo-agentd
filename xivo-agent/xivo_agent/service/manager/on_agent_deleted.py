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

class OnAgentDeletedManager(object):

    def __init__(self, step_factory):
        self._get_agent_status = step_factory.get_agent_status()
        self._remove_agent_from_queues = step_factory.remove_agent_from_queues()
        self._update_queue_log = step_factory.update_queue_log()
        self._update_agent_status = step_factory.update_agent_status()
        self._send_agent_logoff_event = step_factory.send_agent_logoff_event()

    def on_agent_deleted(self, agent_id):
        agent_status = self._get_agent_status.get_status(agent_id)
        if agent_status is None:
            return

        self._remove_agent_from_queues.remove_agent_from_queues(agent_status)
        self._update_queue_log.log_off_agent(agent_status)
        self._update_agent_status.log_off_agent(agent_status.agent_id)
        self._send_agent_logoff_event.send_agent_logoff(agent_status.agent_id, agent_status.agent_number)
