# Copyright 2013-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_agent.exception import AgentAlreadyInQueueError
from xivo_dao.helpers import db_utils


class AddMemberManager:

    def __init__(self, add_to_queue_action, ami_client, agent_status_dao, queue_member_dao):
        self._add_to_queue_action = add_to_queue_action
        self._ami_client = ami_client
        self._agent_status_dao = agent_status_dao
        self._queue_member_dao = queue_member_dao

    def add_agent_to_queue(self, agent, queue):
        self._check_agent_is_not_member_of_queue(agent, queue)
        self._add_queue_member(agent, queue)
        self._send_agent_added_event(agent, queue)
        self._add_to_queue_if_logged(agent, queue)

    def _check_agent_is_not_member_of_queue(self, agent, queue):
        for agent_queue in agent.queues:
            if agent_queue.name == queue.name:
                raise AgentAlreadyInQueueError()

    def _add_queue_member(self, agent, queue):
        with db_utils.session_scope():
            self._queue_member_dao.add_agent_to_queue(agent.id, agent.number, queue.name)

    def _send_agent_added_event(self, agent, queue):
        self._ami_client.agent_added_to_queue(agent.id, agent.number, queue.name)

    def _add_to_queue_if_logged(self, agent, queue):
        with db_utils.session_scope():
            agent_status = self._agent_status_dao.get_status(agent.id)
        if agent_status is not None:
            self._add_to_queue_action.add_agent_to_queue(agent_status, queue)
