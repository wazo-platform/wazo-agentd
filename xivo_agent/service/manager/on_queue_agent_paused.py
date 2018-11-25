# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import logging

from xivo_dao.helpers import db_utils
from xivo_bus.resources.common.event import ArbitraryEvent

logger = logging.getLogger(__name__)


class OnQueueAgentPausedManager(object):

    def __init__(self, agent_status_dao, user_dao, bus_publisher):
        self._agent_status_dao = agent_status_dao
        self._user_dao = user_dao
        self._bus_publisher = bus_publisher

    def on_queue_agent_paused(self, agent_id, agent_number, reason, queue):
        self._db_update_agent_status(agent_id, True, reason)
        bus_event = self._new_agent_paused_event(agent_id, agent_number, reason, queue)
        self._send_bus_status_update(bus_event, agent_id)

    def on_queue_agent_unpaused(self, agent_id, agent_number, reason, queue):
        self._db_update_agent_status(agent_id, False, reason)
        bus_event = self._new_agent_unpaused_event(agent_id, agent_number, reason, queue)
        self._send_bus_status_update(bus_event, agent_id)

    def _new_agent_paused_event(self, id_, number, reason, queue):
        return self._create_bus_event('agent_paused', 'status.agent.pause', True,
                                      id_, number, reason, queue)

    def _new_agent_unpaused_event(self, id_, number, reason, queue):
        return self._create_bus_event('agent_unpaused', 'status.agent.unpause', False,
                                      id_, number, reason, queue)

    def _db_update_agent_status(self, agent_id, is_paused, reason):
        with db_utils.session_scope():
            self._agent_status_dao.update_pause_status(agent_id, is_paused, reason)

    def _create_bus_event(self, name, routing_key, is_paused, id_, number, reason, queue):
        body = {
            'agent_id': id_,
            'agent_number': number,
            'queue': queue,
            'paused': is_paused,
            'paused_reason': reason
        }

        bus_event = ArbitraryEvent(
            name=name,
            body=body,
            required_acl='events.statuses.agents'
        )
        bus_event.routing_key = routing_key

        return bus_event

    def _send_bus_status_update(self, event, agent_id):
        with db_utils.session_scope():
            logger.debug('Looking for users with agent id %s...', agent_id)
            users = self._user_dao.find_all_by_agent_id(agent_id)
            logger.debug('Found %s users.', len(users))
            headers = {'user_uuid:{uuid}'.format(uuid=user.uuid): True for user in users}
            headers['agent_id:{id}'.format(id=str(agent_id))] = True
            self._bus_publisher.publish(event, headers=headers)
