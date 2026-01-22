# Copyright 2013-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import db_utils

from wazo_agentd.exception import AgentNotInQueueError


class RemoveMemberManager:
    def __init__(self, remove_from_queue_action, amid_client, queue_member_dao):
        self._remove_from_queue_action = remove_from_queue_action
        self._amid_client = amid_client
        self._queue_member_dao = queue_member_dao

    def remove_agent_from_queue(self, agent, queue):
        self._check_agent_is_member_of_queue(agent, queue)
        self._remove_queue_member(agent, queue)
        self._send_agent_removed_event(agent, queue)
        self._remove_from_queue(agent, queue)

    def _check_agent_is_member_of_queue(self, agent, queue):
        for agent_queue in agent.queues:
            if agent_queue.name == queue.name:
                return
        raise AgentNotInQueueError()

    def _remove_queue_member(self, agent, queue):
        with db_utils.session_scope():
            self._queue_member_dao.remove_agent_from_queue(agent.id, queue.name)

    def _send_agent_removed_event(self, agent, queue):
        self._amid_client.action(
            'UserEvent',
            {
                'UserEvent': 'AgentRemovedFromQueue',
                'AgentID': agent.id,
                'AgentNumber': agent.number,
                'QueueName': queue.name,
            },
        )

    def _remove_from_queue(self, agent, queue):
        self._remove_from_queue_action.remove_agent_from_queue(agent, queue)
