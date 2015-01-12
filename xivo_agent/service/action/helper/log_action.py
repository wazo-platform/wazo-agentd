# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from xivo_agent.exception import MissingConfigurationError
from xivo_bus.resources.cti.event import AgentStatusUpdateEvent


class LogActionMixin(object):

    def __init__(self, bus_producer, config):
        self._bus_producer = bus_producer

        try:
            self._uuid = config['uuid']
            self._exchange_name = config['bus']['exchange_name']
            self._exchange_type = config['bus']['exchange_type']
            self._exchange_durable = config['bus']['exchange_durable']
            self._routing_key = config['bus']['routing_keys']['agent_status']
        except KeyError as e:
            raise MissingConfigurationError(str(e))

        self._bus_producer.declare_exchange(self._exchange_name,
                                            self._exchange_type,
                                            self._exchange_durable)

    def _send_bus_status_update(self, agent_id):
        msg = AgentStatusUpdateEvent(self._uuid, agent_id, self.agent_status)
        self._bus_producer.publish_event(self._exchange_name,
                                         self._routing_key,
                                         msg)
