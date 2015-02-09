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

from mock import Mock, ANY, sentinel

from xivo_bus import Marshaler
from xivo_bus.resources.cti.event import AgentStatusUpdateEvent

from xivo_agent.queuelog import QueueLogManager
from xivo_agent.service.action.login import LoginAction
from xivo_agent.service.helper import format_agent_skills


class TestLoginAction(unittest.TestCase):

    def setUp(self):
        self.ami_client = Mock()
        self.queue_log_manager = Mock(QueueLogManager)
        self.agent_status_dao = Mock()
        self.line_dao = Mock()
        self.config = {
            'bus': {
                'username': 'guest',
                'password': 'guest',
                'host': 'localhost',
                'port': 1234,
                'exchange_name': sentinel.exchange_name,
                'exchange_type': sentinel.exchange_type,
                'exchange_durable': sentinel.exchange_durable,
                'routing_keys': {
                    'agent_status': sentinel.agent_status_routing_key,
                },
            },
            'uuid': 'my-uuid',
        }
        self.publish_event = Mock()
        self.login_action = LoginAction(self.ami_client,
                                        self.queue_log_manager,
                                        self.agent_status_dao,
                                        self.line_dao,
                                        self.config,
                                        self.publish_event)
        self.marshaler = Marshaler('my-uuid')

    def test_login_agent(self):
        agent_id = 10
        agent_number = '10'
        queue = Mock()
        agent = Mock()
        agent.id = agent_id
        agent.number = agent_number
        agent.queues = [queue]
        extension = '1001'
        context = 'default'
        state_interface = 'SIP/abcd'
        skills = format_agent_skills(agent_id)

        self.line_dao.get_interface_from_exten_and_context.return_value = state_interface

        self.login_action.login_agent(agent, extension, context)

        self.agent_status_dao.log_in_agent.assert_called_once_with(agent_id, agent_number, extension, context, ANY, state_interface)
        self.agent_status_dao.add_agent_to_queues.assert_called_once_with(agent_id, agent.queues)
        self.queue_log_manager.on_agent_logged_in.assert_called_once_with(agent_number, extension, context)
        self.ami_client.queue_add.assert_called_once_with(queue.name, ANY, ANY, state_interface, queue.penalty, skills)
        self.ami_client.agent_login.assert_called_once_with(agent_id, agent_number, extension, context)
        self.publish_event.assert_called_once_with(
            self.marshaler.marshal_message(AgentStatusUpdateEvent('my-uuid', 10, 'logged_in')),
            routing_key=sentinel.agent_status_routing_key,
        )
