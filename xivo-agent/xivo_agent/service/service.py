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

import logging
from xivo_agent.ctl import commands
from xivo_agent.service.blackboard import Blackboard

logger = logging.getLogger(__name__)


class AgentService(object):

    def __init__(self, agent_server):
        self._agent_server = agent_server
        self._steps = {}

    def init(self, step_factory):
        self._add_login_cmd(step_factory)
        self._add_logoff_cmd(step_factory)
        self._add_status_command(step_factory)

    def run(self):
        while True:
            self._agent_server.process_next_command()

    def _add_login_cmd(self, step_factory):
        steps = [
            step_factory.get_agent(),
            step_factory.get_agent_status(),
            step_factory.check_agent_is_not_logged(),
            step_factory.check_extension_is_not_in_use(),
            step_factory.get_interface_for_extension(),
            step_factory.update_agent_status(),
            step_factory.update_queue_log(),
            step_factory.add_agent_to_queues(),
            step_factory.send_agent_login_event(),
        ]
        self._add_cmd(commands.LoginCommand, self._exec_login_cmd, steps)

    def _add_logoff_cmd(self, step_factory):
        steps = [
            step_factory.get_agent(),
            step_factory.get_agent_status(),
            step_factory.check_agent_is_logged(),
            step_factory.remove_agent_from_queues(),
            step_factory.update_queue_log(),
            step_factory.update_agent_status(),
            step_factory.send_agent_logoff_event(),
        ]
        self._add_cmd(commands.LogoffCommand, self._exec_logoff_cmd, steps)

    def _add_status_command(self, step_factory):
        steps = [
            step_factory.get_agent(),
            step_factory.get_agent_status(),
        ]
        self._add_cmd(commands.StatusCommand, self._exec_status_cmd, steps)

    def _add_cmd(self, cmd_class, callback, steps):
        self._steps[cmd_class.name] = steps
        self._agent_server.add_command(cmd_class, callback)

    def _exec_login_cmd(self, login_cmd, response):
        logger.info('Executing login command with ID %s on %s@%s', login_cmd.agent_id, login_cmd.extension, login_cmd.context)
        blackboard = Blackboard()
        blackboard.extension = login_cmd.extension
        blackboard.context = login_cmd.context

        self._exec_cmd(login_cmd, response, blackboard)

    def _exec_logoff_cmd(self, logoff_cmd, response):
        logger.info('Executing logoff command with ID %s', logoff_cmd.agent_id)
        blackboard = Blackboard()

        self._exec_cmd(logoff_cmd, response, blackboard)

    def _exec_status_cmd(self, status_cmd, response):
        logger.info('Executing status command with ID %s', status_cmd.agent_id)
        blackboard = Blackboard()

        self._exec_cmd(status_cmd, response, blackboard)

        if not response.error:
            is_logged = blackboard.agent_status is not None
            response.value = {'logged': is_logged}

    def _exec_cmd(self, cmd, response, blackboard):
        steps = self._steps[cmd.name]
        for step in steps:
            logger.debug('Executing step %s', step)
            step.execute(cmd, response, blackboard)
            if response.error:
                logger.debug('Step %s returned error %s', step, response.error)
                break
