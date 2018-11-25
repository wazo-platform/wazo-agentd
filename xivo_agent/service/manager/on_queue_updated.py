# Copyright 2013-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers import db_utils


class OnQueueUpdatedManager:

    def __init__(self, add_to_queue_action, remove_from_queue_action, agent_status_dao):
        self._add_to_queue_action = add_to_queue_action
        self._remove_from_queue_action = remove_from_queue_action
        self._agent_status_dao = agent_status_dao

    def on_queue_updated(self, queue):
        with db_utils.session_scope():
            added_agent_statuses = self._agent_status_dao.get_statuses_to_add_to_queue(queue.id)
            removed_agent_statuses = self._agent_status_dao.get_statuses_to_remove_from_queue(queue.id)

        self._manage_added_agents(added_agent_statuses, queue)
        self._manage_removed_agents(removed_agent_statuses, queue)

    def _manage_added_agents(self, agent_statuses, queue):
        for agent_status in agent_statuses:
            self._add_to_queue_action.add_agent_to_queue(agent_status, queue)

    def _manage_removed_agents(self, agent_statuses, queue):
        for agent_status in agent_statuses:
            self._remove_from_queue_action.remove_agent_from_queue(agent_status, queue)
