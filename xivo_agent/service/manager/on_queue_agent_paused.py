# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers import db_utils
from xivo_bus.resources.common.event import ArbitraryEvent


class OnQueueAgentPausedManager(object):

    def __init__(self, agent_status_dao, bus_publisher):
        self._agent_status_dao = agent_status_dao
        self._bus_publisher = bus_publisher

    def on_queue_agent_paused(self, msg):
        name = 'agent_paused'
        routing_key = 'status.agent.pause'
        is_paused = True
        self._send_bus_status_update(self._create_bus_event(name, routing_key, is_paused, msg))

    def on_queue_agent_unpaused(self, msg):
        name = 'agent_unpaused'
        routing_key = 'status.agent.unpause'
        is_paused = False
        self._send_bus_status_update(self._create_bus_event(name, routing_key, is_paused, msg))

    def _create_bus_event(self, name, routing_key, is_paused, msg):
        _, agent_number = msg['MemberName'].split('/')
        reason = msg['PausedReason']

        with db_utils.session_scope():
            agent_status = self._agent_status_dao.get_status_by_number(agent_number)
            self._agent_status_dao.update_pause_status(agent_status.agent_id, is_paused, reason)

        body = {
            'agent_id': agent_status.agent_id,
            'agent_number': agent_status.agent_number,
            'queue': msg['Queue'],
            'paused': is_paused,
            'pausedReason': reason
        }

        bus_event = ArbitraryEvent(
            name=name,
            body=body,
            required_acl='events.statuses.agents'
        )
        bus_event.routing_key = routing_key

        return bus_event

    def _send_bus_status_update(self, event):
        self._bus_publisher.publish(event)
