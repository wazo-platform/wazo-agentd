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

from mock import Mock
from mock import sentinel

from xivo_bus.resources.cti.event import AgentStatusUpdateEvent
from xivo_agent.service.manager.logoff import LogoffManager


class TestLogoffManager(unittest.TestCase):

    def setUp(self):
        self.logoff_action = Mock()
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

        self.logoff_manager = LogoffManager(self.logoff_action,
                                            self.agent_status_dao,
                                            self.bus_producer,
                                            self.config)

    def test_logoff_agent(self):
        agent_status = Mock(agent_id=42)

        self.logoff_manager.logoff_agent(agent_status)

        self.logoff_action.logoff_agent.assert_called_once_with(agent_status)
        expected_bus_msg = AgentStatusUpdateEvent(sentinel.uuid, 42, 'logged_out')
        self.bus_producer.publish_event.assert_called_once_with(
            sentinel.exchange_name,
            sentinel.agent_status_routing_key,
            expected_bus_msg,
        )
