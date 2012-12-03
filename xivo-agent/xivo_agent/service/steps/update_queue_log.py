# -*- coding: UTF-8 -*-

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
