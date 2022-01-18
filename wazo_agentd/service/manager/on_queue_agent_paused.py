# Copyright 2017-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from xivo_dao.helpers import db_utils
from xivo_bus.resources.agent.event import PauseAgentEvent, UnpauseAgentEvent

logger = logging.getLogger(__name__)


class OnQueueAgentPausedManager:
    def __init__(self, agent_status_dao, user_dao, bus_publisher):
        self._agent_status_dao = agent_status_dao
        self._user_dao = user_dao
        self._bus_publisher = bus_publisher

    def on_queue_agent_paused(self, agent_id, agent_number, reason, queue):
        self._db_update_agent_status(agent_id, True, reason)
        event = PauseAgentEvent(agent_id, agent_number, queue, reason)
        self._send_bus_status_update(event, agent_id)

    def on_queue_agent_unpaused(self, agent_id, agent_number, reason, queue):
        self._db_update_agent_status(agent_id, False, reason)
        event = UnpauseAgentEvent(agent_id, agent_number, queue, reason)
        self._send_bus_status_update(event, agent_id)

    def _db_update_agent_status(self, agent_id, is_paused, reason):
        with db_utils.session_scope():
            self._agent_status_dao.update_pause_status(agent_id, is_paused, reason)

    def _send_bus_status_update(self, event, agent_id):
        with db_utils.session_scope():
            logger.debug('Looking for users with agent id %s...', agent_id)
            users = self._user_dao.find_all_by_agent_id(agent_id)
            logger.debug('Found %s users.', len(users))
            headers = {
                'user_uuid:{uuid}'.format(uuid=user.uuid): True for user in users
            }
            headers['agent_id:{id}'.format(id=str(agent_id))] = True
            self._bus_publisher.publish_soon(event, headers=headers)
