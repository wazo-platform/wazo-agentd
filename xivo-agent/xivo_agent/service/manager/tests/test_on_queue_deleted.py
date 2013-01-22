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
from xivo_agent.service.manager.on_queue_deleted import OnQueueDeletedManager


class TestOnQueueDeletedManager(unittest.TestCase):

    def setUp(self):
        step_factory = Mock(StepFactory)

        self.update_agent_status = Mock()

        step_factory.update_agent_status.return_value = self.update_agent_status

        self.on_queue_deleted_manager = OnQueueDeletedManager(step_factory)

    def test_on_queue_deleted(self):
        queue_id = 42

        self.on_queue_deleted_manager.on_queue_deleted(queue_id)

        self.update_agent_status.remove_all_agents_from_queue.assert_called_once_with(queue_id)
