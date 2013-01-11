# -*- coding: UTF-8 -*-

# Copyright (C) 2013  Avencall
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
from xivo_agent.service.factory import StepFactory
from xivo_agent.service.manager.on_agent_deleted import OnAgentDeletedManager

class TestOnAgentDeletedManager(unittest.TestCase):

    def test_on_agent_deleted(self):
        step_factory = Mock(StepFactory)

        get_agent_status = Mock()
        remove_agent_from_queues = Mock()
        update_queue_log = Mock()
        update_agent_status = Mock()
        send_agent_logoff_event = Mock()

        step_factory.get_agent_status.return_value = get_agent_status
        step_factory.remove_agent_from_queues.return_value = remove_agent_from_queues
        step_factory.update_queue_log.return_value = update_queue_log
        step_factory.update_agent_status.return_value = update_agent_status
        step_factory.send_agent_logoff_event.return_value = send_agent_logoff_event

        agent_id = 1
        agent_number = '2'

        agent_status = Mock()
        agent_status.agent_id = agent_id
        agent_status.agent_number = agent_number

        get_agent_status.get_status.return_value = agent_status

        on_agent_deleted_manager = OnAgentDeletedManager(step_factory)

        on_agent_deleted_manager.on_agent_deleted(agent_id)

        get_agent_status.get_status.assert_alled_once_with(agent_id)
        remove_agent_from_queues.remove_agent_from_queues.assert_alled_once_with(agent_status)
        update_queue_log.log_off_agent.assert_called_once_with(agent_status)
        update_agent_status.log_off_agent.assert_called_once_with(agent_id)
        send_agent_logoff_event.send_agent_logoff.assert_called_once_with(agent_id, agent_number)
