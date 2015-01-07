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

import unittest

from functools import partial
from mock import Mock
from mock import sentinel

from xivo_bus.resources.cti.event import AgentStatusUpdateEvent
from xivo_agent.service.manager.login import LoginManager
from xivo_agent.exception import MissingConfigurationError


class TestLoginManager(unittest.TestCase):

    def setUp(self):
        self.login_action = Mock()
        self.agent_status_dao = Mock()
        self.bus_producer = Mock()
        self.config = {
            'bus': {
                'exchange_name': sentinel.exchange_name,
                'exchange_type': sentinel.exchange_type,
                'exchange_durable': sentinel.exchange_durable,
                'routing_keys': {
                    'agent_status': sentinel.agent_status_routing_key,
                },
            },
            'uuid': sentinel.uuid,
        }
        self.login_manager = LoginManager(self.login_action,
                                          self.agent_status_dao,
                                          self.bus_producer,
                                          self.config)
        self.bus_producer.reset_mock()

    def test_login_agent(self):
        agent = Mock(id=42)
        extension = '1001'
        context = 'default'
        self.agent_status_dao.get_status.return_value = None
        self.agent_status_dao.is_extension_in_use.return_value = False

        self.login_manager.login_agent(agent, extension, context)

        self.login_action.login_agent.assert_called_once_with(agent, extension, context)
        expected_bus_msg = AgentStatusUpdateEvent(sentinel.uuid, 42, 'logged_in')
        self.bus_producer.publish_event.assert_called_once_with(
            sentinel.exchange_name,
            sentinel.agent_status_routing_key,
            expected_bus_msg,
        )

    def test_missing_configuration_options(self):
        init = partial(LoginManager, self.login_action, self.agent_status_dao, self.bus_producer)

        config = dict(self.config)
        config.pop('bus')
        self.assertRaises(MissingConfigurationError, init, config)

        config = dict(self.config)
        config.pop('uuid')
        self.assertRaises(MissingConfigurationError, init, config)
