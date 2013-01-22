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

class OnAgentUpdatedManager(object):

    def __init__(self, step_factory):
        self._get_agent_status = step_factory.get_agent_status()
        self._get_agent = step_factory.get_agent()
        self._add_agent_to_queue = step_factory.add_agent_to_queue()
        self._remove_agent_from_queue = step_factory.remove_agent_from_queue()
        self._update_agent_status = step_factory.update_agent_status()

    def on_agent_updated(self, agent_id):
        agent_status = self._get_agent_status.get_status(agent_id)
        if agent_status is None:
            return

        queue_delta = self._calculate_queue_delta(agent_id, agent_status)

        self._manage_added_queues(agent_status, queue_delta.added)
        self._manage_removed_queues(agent_status, queue_delta.removed)

    def _calculate_queue_delta(self, agent_id, agent_status):
        agent = self._get_agent.get_agent_with_id(agent_id)
        return QueueDelta.calculate(agent_status.queues, agent.queues)

    def _manage_added_queues(self, agent_status, added_queues):
        for queue in added_queues:
            self._add_agent_to_queue.add_agent_to_queue(agent_status, queue.name)
            self._update_agent_status.add_agent_to_queue(agent_status.agent_id, queue)

    def _manage_removed_queues(self, agent_status, removed_queues):
        for queue in removed_queues:
            self._remove_agent_from_queue.remove_agent_from_queue(agent_status, queue.name)
            self._update_agent_status.remove_agent_from_queue(agent_status.agent_id, queue.id)


class QueueDelta(object):

    def __init__(self, added, removed):
        self.added = added
        self.removed = removed

    @classmethod
    def calculate(cls, old_queues, new_queues):
        old_queues_by_id = dict((q.id, q) for q in old_queues)
        new_queues_by_id = dict((q.id, q) for q in new_queues)

        added_ids = set(new_queues_by_id).difference(old_queues_by_id)
        removed_ids = set(old_queues_by_id).difference(new_queues_by_id)

        added_queues = [new_queues_by_id[queue_id] for queue_id in added_ids]
        removed_queues = [old_queues_by_id[queue_id] for queue_id in removed_ids]

        return cls(added_queues, removed_queues)
