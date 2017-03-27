# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers import db_utils
from xivo_bus.resources.common.event import ArbitraryEvent


class OnQueueAgentCallChangedManager(object):

    def __init__(self, agent_status_dao, bus_publisher):
        self._agent_status_dao = agent_status_dao
        self._bus_publisher = bus_publisher

    def on_queue_call_status_changed(self, agent_id, agent_number, queue, on_call):
        self._db_update_agent_call_status(agent_id, on_call)
        bus_event = self._agent_call_changed_event(agent_id, agent_number, queue, on_call)
        self._send_bus_status_update(bus_event)

    def _agent_call_changed_event(self, id_, number, queue, on_call):
        return self._create_bus_event('agent_call_changed', 'status.agent.pause', on_call,
                                      id_, number, queue)

    def _db_update_agent_call_status(self, agent_id, on_call):
        with db_utils.session_scope():
            self._agent_status_dao.update_on_call_status(agent_id, on_call)

    def _create_bus_event(self, name, routing_key, on_call, id_, number, queue):
        body = {
            'agent_id': id_,
            'agent_number': number,
            'queue': queue,
            'on_call': on_call,
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
