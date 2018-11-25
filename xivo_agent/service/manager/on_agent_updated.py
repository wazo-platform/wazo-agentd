# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+


class OnAgentUpdatedManager(object):

    def __init__(self, add_to_queue_action, remove_from_queue_action, update_penalty_action, agent_status_dao):
        self._add_to_queue_action = add_to_queue_action
        self._remove_from_queue_action = remove_from_queue_action
        self._update_penalty_action = update_penalty_action
        self._agent_status_dao = agent_status_dao

    def on_agent_updated(self, agent):
        agent_status = self._agent_status_dao.get_status(agent.id)
        if agent_status is None:
            return

        queue_delta = self._calculate_queue_delta(agent_status, agent)

        self._manage_added_queues(agent_status, queue_delta.added)
        self._manage_removed_queues(agent_status, queue_delta.removed)
        self._manage_penalty_updated(agent_status, queue_delta.penalty_updated)

    def _calculate_queue_delta(self, agent_status, agent):
        return QueueDelta.calculate(agent_status.queues, agent.queues)

    def _manage_added_queues(self, agent_status, added_queues):
        for queue in added_queues:
            self._add_to_queue_action.add_agent_to_queue(agent_status, queue)

    def _manage_penalty_updated(self, agent_status, updated_queues):
        for queue in updated_queues:
            self._update_penalty_action.update(agent_status, queue)

    def _manage_removed_queues(self, agent_status, removed_queues):
        for queue in removed_queues:
            self._remove_from_queue_action.remove_agent_from_queue(agent_status, queue)


class QueueDelta(object):

    def __init__(self, added, removed, penalty_updated):
        self.added = added
        self.removed = removed
        self.penalty_updated = penalty_updated

    @classmethod
    def calculate(cls, old_queues, new_queues):
        old_queues_by_id = dict((q.id, q) for q in old_queues)
        new_queues_by_id = dict((q.id, q) for q in new_queues)
        updated_ids = set(new_queues_by_id).intersection(old_queues_by_id)

        added_ids = set(new_queues_by_id).difference(old_queues_by_id)
        removed_ids = set(old_queues_by_id).difference(new_queues_by_id)
        penalty_updated = [new_queues_by_id[queue_id] for queue_id in updated_ids if
                           new_queues_by_id[queue_id].penalty != old_queues_by_id[queue_id].penalty]

        added_queues = [new_queues_by_id[queue_id] for queue_id in added_ids]
        removed_queues = [old_queues_by_id[queue_id] for queue_id in removed_ids]

        return cls(added_queues, removed_queues, penalty_updated)
