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

import datetime
import unittest

from mock import Mock, ANY

from xivo_bus.resources.cti.event import AgentStatusUpdateEvent

from xivo_agent.service.action.logoff import LogoffAction


class TestLogoffAction(unittest.TestCase):

    def setUp(self):
        self.ami_client = Mock()
        self.queue_log_manager = Mock()
        self.agent_status_dao = Mock()
        self.bus_publisher = Mock()
        self.logoff_action = LogoffAction(self.ami_client,
                                          self.queue_log_manager,
                                          self.agent_status_dao,
                                          self.bus_publisher)

    def test_logoff_agent(self):
        agent_id = 10
        agent_number = '10'
        queue_name = 'q1'
        queue = Mock()
        queue.name = queue_name
        agent_status = Mock()
        agent_status.agent_id = agent_id
        agent_status.agent_number = agent_number
        agent_status.login_at = datetime.datetime.now()
        agent_status.queues = [queue]

        self.logoff_action.logoff_agent(agent_status)

        self.ami_client.agent_logoff.assert_called_once_with(agent_id, agent_number)
        self.ami_client.queue_remove.assert_called_once_with(queue_name, agent_status.interface)
        self.queue_log_manager.on_agent_logged_off.assert_called_once_with(agent_number, agent_status.extension,
                                                                           agent_status.context, ANY)
        self.agent_status_dao.remove_agent_from_all_queues.assert_called_once_with(agent_id)
        self.agent_status_dao.log_off_agent(agent_id)
        self.bus_publisher.publish.assert_called_once_with(
            AgentStatusUpdateEvent(10, AgentStatusUpdateEvent.STATUS_LOGGED_OUT),
        )
