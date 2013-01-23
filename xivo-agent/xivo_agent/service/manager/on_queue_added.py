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

class OnQueueAddedManager(object):

    def __init__(self, step_factory):
        self._get_queue = step_factory.get_queue()
        self._get_agent_statuses = step_factory.get_agent_statuses()
        self._add_agent_to_queue = step_factory.add_agent_to_queue()
        self._update_agent_status = step_factory.update_agent_status()

    def on_queue_added(self, queue_id):
        queue = self._get_queue.get_queue(queue_id)

        agent_statuses = self._get_agent_statuses.get_statuses_for_queue(queue_id)
        for agent_status in agent_statuses:
            self._add_agent_to_queue.add_agent_to_queue(agent_status, queue.name)
            self._update_agent_status.add_agent_to_queue(agent_status.agent_id, queue)
