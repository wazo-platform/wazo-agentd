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
import logging
from xivo_agent.ctl import commands
from xivo_agent.ctl import error

logger = logging.getLogger(__name__)


class AgentService(object):

    def __init__(self, ami_client, agent_server, queue_log_manager, agent_login_dao, agentfeatures_dao):
        self._ami_client = ami_client
        self._agent_server = agent_server
        self._queue_log_manager = queue_log_manager
        self._agent_login_dao = agent_login_dao
        self._agentfeatures_dao = agentfeatures_dao

    def init(self):
        self._agent_server.add_command(commands.LoginCommand, self._exec_login_cmd)
        self._agent_server.add_command(commands.LogoffCommand, self._exec_logoff_cmd)
        self._agent_server.add_command(commands.StatusCommand, self._exec_status_cmd)

    def run(self):
        while True:
            self._agent_server.process_next_command()

    def _validate_login_command(self, login_cmd, response):
        if self._is_extension_in_use(login_cmd.extension, login_cmd.context):
            response.error = error.ALREADY_IN_USE
        elif self._is_agent_logged_in(login_cmd.agent_id):
            response.error = error.ALREADY_LOGGED

    def _exec_login_cmd(self, login_cmd, response):
        self._validate_login_command(login_cmd, response)
        if not response.error:
            agent = self._agent_with_id(login_cmd.agent_id)
            self._log_in_agent(agent, login_cmd.extension, login_cmd.context)

    def _exec_logoff_cmd(self, logoff_cmd, response):
        agent = self._agent_with_id(logoff_cmd.agent_id)
        if self._is_agent_logged_in(agent.id):
            self._log_off_agent(agent)
        else:
            response.error = error.NOT_LOGGED

    def _exec_status_cmd(self, status_cmd, response):
        logged = self._is_agent_logged_in(status_cmd.agent_id)
        response.value = {'logged': logged}

    def _agent_with_id(self, agent_id):
        return self._agentfeatures_dao.agent_with_id(agent_id)

    def _is_extension_in_use(self, extension, context):
        return self._agent_login_dao.is_extension_in_use(extension, context)

    def _is_agent_logged_in(self, agent_id):
        return self._agent_login_dao.is_agent_logged_in(agent_id)

    def _log_in_agent(self, agent, extension, context):
        interface = 'Local/%s@%s' % (extension, context)
        member_name = 'Agent/%s' % agent.number

        self._agent_login_dao.log_in_agent(agent.id, extension, context)

        self._queue_log_manager.on_agent_logged_in(agent.number, extension, context)

        for queue in agent.queues:
            action = self._ami_client.queue_add(queue.name, interface, member_name)
            if not action.success:
                logger.warning('Failure to add interface %r to queue %r', interface, queue.name)

    def _log_off_agent(self, agent):
        agent_login_status = self._agent_login_dao.get_status(agent.id)
        login_time = self._compute_login_time(agent_login_status.login_at)
        interface = 'Local/%s@%s' % (agent_login_status.extension, agent_login_status.context)

        for queue in agent.queues:
            self._ami_client.queue_remove(queue.name, interface)

        self._queue_log_manager.on_agent_logged_off(agent.number, agent_login_status.extension,
                                                    agent_login_status.context, login_time)

        self._agent_login_dao.log_off_agent(agent.id)

    def _compute_login_time(self, login_at):
        delta = datetime.datetime.now() - login_at
        return self._timedelta_to_seconds(delta)

    def _timedelta_to_seconds(self, delta):
        return delta.days * 60 * 60 * 24 + delta.seconds
