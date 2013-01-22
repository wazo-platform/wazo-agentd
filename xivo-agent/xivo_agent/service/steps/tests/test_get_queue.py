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
from xivo_agent.ctl import error
from xivo_agent.service.steps import GetQueueStep


class TestGetQueueStep(unittest.TestCase):

    def test_execute_when_queue_exist(self):
        command = Mock()
        command.queue_id = 12
        response = Mock()
        blackboard = Mock()

        queue_name = 'queue1'
        queue_dao = Mock()
        queue_dao.queue_name.return_value = queue_name

        step = GetQueueStep(queue_dao)
        step.execute(command, response, blackboard)

        queue_dao.queue_name.assert_called_once_with(command.queue_id)
        self.assertEqual(blackboard.queue.name, queue_name)

    def test_execute_when_queue_doesnt_exit(self):
        command = Mock()
        command.queue_id = 12
        response = Mock()
        blackboard = Mock()

        queue_dao = Mock()
        queue_dao.queue_name.side_effect = LookupError()

        step = GetQueueStep(queue_dao)
        step.execute(command, response, blackboard)

        queue_dao.queue_name.assert_called_once_with(command.queue_id)
        self.assertEqual(response.error, error.NO_SUCH_QUEUE)
