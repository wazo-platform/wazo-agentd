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

from datetime import datetime
from mock import Mock, ANY
from xivo_agent.service.steps.update_queue_log import UpdateQueueLogStep


class TestUpdateQueueLogStep(unittest.TestCase):

    def setUp(self):
        self.command = Mock()
        self.response = Mock()
        self.response.error = None
        self.blackboard = Mock()
        self.queue = Mock()
        self.queue.name = 'foobar1'
        self.agent_status = Mock()
        self.agent_status.agent_id = 42
        self.agent_status.agent_number = '43'
        self.agent_status.login_at = datetime(2000, 1, 2, 3, 4, 5)
        self.agent_status.queues = [self.queue]
        self.blackboard.agent_status = self.agent_status
        self.queue_log_manager = Mock()
        self.step = UpdateQueueLogStep(self.queue_log_manager)

    def test_log_off_agent(self):
        self.step.log_off_agent(self.agent_status)

        self.queue_log_manager.on_agent_logged_off.assert_called_once_with(self.agent_status.agent_number,
                                                                           self.agent_status.extension,
                                                                           self.agent_status.context,
                                                                           ANY)
