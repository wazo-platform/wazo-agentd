# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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
from xivo_agent.service.manager.on_queue_updated import OnQueueUpdatedManager


class TestOnQueueUpdatedManager(unittest.TestCase):

    def setUp(self):
        step_factory = Mock(StepFactory)

        self.get_queue = Mock()
        self.get_agent_statuses = Mock()
        self.add_agent_to_queue = Mock()
        self.remove_agent_from_queue = Mock()
        self.update_agent_status = Mock()

        step_factory.get_queue.return_value = self.get_queue
        step_factory.get_agent_statuses.return_value = self.get_agent_statuses
        step_factory.add_agent_to_queue.return_value = self.add_agent_to_queue
        step_factory.remove_agent_from_queue.return_value = self.remove_agent_from_queue
        step_factory.update_agent_status.return_value = self.update_agent_status

        self.on_queue_updated_manager = OnQueueUpdatedManager(step_factory)

    def test_on_queue_updated(self):
        queue_id = 1
        queue = Mock()
        queue.id = queue_id
        agent_status1 = Mock()
        agent_status2 = Mock()

        self.get_queue.get_queue.return_value = queue
        self.get_agent_statuses.get_statuses_to_add_to_queue.return_value = [agent_status1]
        self.get_agent_statuses.get_statuses_to_remove_from_queue.return_value = [agent_status2]

        self.on_queue_updated_manager.on_queue_updated(queue_id)

        self.get_queue.get_queue.assert_called_once_with(queue_id)
        self.get_agent_statuses.get_statuses_to_add_to_queue.assert_called_once_with(queue_id)
        self.get_agent_statuses.get_statuses_to_remove_from_queue.assert_called_once_with(queue_id)

        # added
        self.add_agent_to_queue.add_agent_to_queue.assert_called_once_with(agent_status1, queue.name)
        self.update_agent_status.add_agent_to_queue.assert_called_once_with(agent_status1.agent_id, queue)

        # removed
        self.remove_agent_from_queue.remove_agent_from_queue.assert_called_once_with(agent_status2, queue.name)
        self.update_agent_status.remove_agent_from_queue.assert_called_once_with(agent_status2.agent_id, queue.id)
