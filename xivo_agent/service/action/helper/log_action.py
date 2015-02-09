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

from xivo_bus import Marshaler
from xivo_bus.resources.cti.event import AgentStatusUpdateEvent

from xivo_agent.exception import MissingConfigurationError


class LogActionMixin(object):

    def __init__(self, config, bus_publish_fn):
        try:
            self._uuid = config['uuid']
            self._routing_key = config['bus']['routing_keys']['agent_status']
        except KeyError as e:
            raise MissingConfigurationError(str(e))

        self._marshaler = Marshaler(self._uuid)
        self._publish_event = bus_publish_fn

    def _send_bus_status_update(self, agent_id):
        msg = self._marshaler.marshal_message(
            AgentStatusUpdateEvent(self._uuid, agent_id, self.agent_status))
        self._publish_event(msg, routing_key=self._routing_key)
