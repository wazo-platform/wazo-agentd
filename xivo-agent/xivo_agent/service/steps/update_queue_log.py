# -*- coding: UTF-8 -*-

# Copyright (C) 2012  Avencall
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
from xivo_agent.ctl import commands


class UpdateQueueLogStep(object):

    def __init__(self, queue_log_manager):
        self._queue_log_manager = queue_log_manager

    def execute(self, command, response, blackboard):
        if command.name == commands.LoginCommand.name:
            self._queue_log_manager.on_agent_logged_in(blackboard.agent.number, blackboard.extension, blackboard.context)
        elif command.name == commands.LogoffCommand.name:
            login_time = self._compute_login_time(blackboard.agent_status.login_at)
            self._queue_log_manager.on_agent_logged_off(blackboard.agent.number, blackboard.agent_status.extension, blackboard.agent_status.context, login_time)

    def _compute_login_time(self, login_at):
        delta = datetime.datetime.now() - login_at
        return self._timedelta_to_seconds(delta)

    def _timedelta_to_seconds(self, delta):
        return delta.days * 60 * 60 * 24 + delta.seconds
