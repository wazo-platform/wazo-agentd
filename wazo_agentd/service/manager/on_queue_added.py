# Copyright 2013-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import db_utils


class OnQueueAddedManager:
    def __init__(self, add_to_queue_action, agent_status_dao):
        self._add_to_queue_action = add_to_queue_action
        self._agent_status_dao = agent_status_dao

    def on_queue_added(self, queue):
        with db_utils.session_scope():
            agent_statuses = self._agent_status_dao.get_statuses_for_queue(queue.id)
        for agent_status in agent_statuses:
            self._add_to_queue_action.add_agent_to_queue(agent_status, queue)
