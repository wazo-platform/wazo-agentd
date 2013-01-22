# -*- coding: utf-8 -*-

# Copyright (C) 2012-2013 Avencall
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

from xivo_agent.ctl import error


class CheckAgentIsMemberOfQueueStep(object):

    def execute(self, command, response, blackboard):
        queue_name = blackboard.queue.name
        for queue in blackboard.agent.queues:
            if queue.name == queue_name:
                return
        response.error = error.NOT_IN_QUEUE


class CheckAgentIsNotMemberOfQueueStep(object):

    def execute(self, command, response, blackboard):
        queue_name = blackboard.queue.name
        for queue in blackboard.agent.queues:
            if queue.name == queue_name:
                response.error = error.ALREADY_IN_QUEUE
                return
