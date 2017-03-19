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
        self._send_bus_status_update(self._create_bus_event(name, True, msg))

    def on_queue_agent_unpaused(self, msg):
        name = 'agent_unpaused'
        self._send_bus_status_update(self._create_bus_event(name, False, msg))

    def _create_bus_event(self, name, is_paused, msg):
        _, agent_number = msg['MemberName'].split('/')

        print msg

        body = {
            'agent_number': agent_number,
            'queue': msg['Queue'],
            'paused': is_paused,
            'pausedReason': msg['PausedReason']
        }

        bus_event = ArbitraryEvent(
            name=name,
            body=body,
            required_acl='events.statuses.agents'
        )

        bus_event.routing_key = 'status.agent.unpause'

        return bus_event

    def _send_bus_status_update(self, event):
        self._bus_publisher.publish(event)
