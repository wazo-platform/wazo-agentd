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


class RemoveFromQueueAction(object):

    def __init__(self, ami_client, agent_status_dao):
        self._ami_client = ami_client
        self._agent_status_dao = agent_status_dao

    def remove_agent_from_queue(self, agent_status, queue):
        self._update_asterisk(agent_status, queue)
        self._update_agent_status(agent_status, queue)

    def _update_asterisk(self, agent_status, queue):
        self._ami_client.queue_remove(queue.name, agent_status.interface)

    def _update_agent_status(self, agent_status, queue):
        self._agent_status_dao.remove_agent_from_queues(agent_status.agent_id, [queue.id])
