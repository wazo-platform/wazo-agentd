# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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

import logging

from xivo_agent.exception import AgentAlreadyLoggedError, ExtensionAlreadyInUseError
from xivo_bus.resources.cti.event import AgentStatusUpdateEvent
from xivo_agent.exception import MissingConfigurationError

logger = logging.getLogger(__name__)


class LogManagerMixin(object):

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

    def _send_bus_status_update(self, agent):
        msg = AgentStatusUpdateEvent(self._uuid, agent.id, self.agent_status)
        self._bus_producer.publish_event(self._exchange_name,
                                         self._routing_key,
                                         msg)


class LoginManager(LogManagerMixin):

    agent_status = 'logged_in'

    def __init__(self, login_action, agent_status_dao, agent_server, config):
        super(LoginManager, self).__init__(agent_server, config)
        self._login_action = login_action
        self._agent_status_dao = agent_status_dao

    def login_agent(self, agent, extension, context):
        self._check_agent_is_not_logged(agent)
        self._check_extension_is_not_in_use(extension, context)
        self._login_action.login_agent(agent, extension, context)
        self._send_bus_status_update(agent)

    def _check_agent_is_not_logged(self, agent):
        agent_status = self._agent_status_dao.get_status(agent.id)
        if agent_status is not None:
            raise AgentAlreadyLoggedError()

    def _check_extension_is_not_in_use(self, extension, context):
        if self._agent_status_dao.is_extension_in_use(extension, context):
            raise ExtensionAlreadyInUseError()
