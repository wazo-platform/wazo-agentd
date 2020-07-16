# Copyright 2013-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import db_utils


class UpdatePenaltyAction:
    def __init__(self, amid_client, agent_status_dao):
        self._amid_client = amid_client
        self._agent_status_dao = agent_status_dao

    def update(self, agent_status, queue):
        self._update_asterisk(agent_status, queue)
        self._update_agent_status(agent_status, queue)

    def _update_asterisk(self, agent_status, queue):
        self._amid_client.action(
            'QueuePenalty',
            {
                'Queue': queue.name,
                'Interface': agent_status.interface,
                'Penalty': queue.penalty,
            },
        )

    def _update_agent_status(self, agent_status, queue):
        with db_utils.session_scope():
            self._agent_status_dao.update_penalty(
                agent_status.agent_id, queue.id, queue.penalty
            )
