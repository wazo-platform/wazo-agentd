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
from xivo_agent import dao
from xivo_agent.ctl import commands
from xivo_agent.ctl import error

logger = logging.getLogger(__name__)


class AgentService(object):

    def __init__(self, ami_client, agent_server, queue_log_manager, agent_login_dao):
        self._ami_client = ami_client
        self._agent_server = agent_server
        self._queue_log_manager = queue_log_manager
        self._agent_login_dao = agent_login_dao

    def init(self):
        self._agent_server.add_command(commands.LoginCommand, self._exec_login_cmd)
        self._agent_server.add_command(commands.LogoffCommand, self._exec_logoff_cmd)
        self._agent_server.add_command(commands.StatusCommand, self._exec_status_cmd)

    def run(self):
        while True:
            self._agent_server.process_next_command()

    def _exec_login_cmd(self, login_cmd, response):
        # TODO don't log 2 agents on the same interface (this would be easier if
        #      it was in postgres than ast db)
        agent = dao.agent_with_id(login_cmd.agent_id)
        if self._is_agent_logged_in(agent):
            response.error = error.ALREADY_LOGGED
        else:
            self._log_in_agent(agent, login_cmd.extension, login_cmd.context)

    def _is_agent_logged_in(self, agent):
        return self._agent_login_dao.is_agent_logged_in(agent.id)

    def _log_in_agent(self, agent, extension, context):
        interface = 'Local/%s@%s' % (extension, context)
        member_name = 'Agent/%s' % agent.id

        self._ami_client.db_put('xivo/agents', agent.id, interface)

        self._agent_login_dao.log_in_agent(agent.id, interface)

        for queue in agent.queues:
            action = self._ami_client.queue_add(queue.name, interface, member_name)
            if not action.success:
                logger.warning('Failure to add interface %r to queue %r', interface, queue.name)

    def _exec_logoff_cmd(self, logoff_cmd, response):
        agent = dao.agent_with_id(logoff_cmd.agent_id)

        action = self._ami_client.db_get('xivo/agents', agent.id)
        if action.success:
            # agent is logged
            interface = action.val
            for queue in agent.queues:
                action = self._ami_client.queue_remove(queue.name, interface)
            self._ami_client.db_del('xivo/agents', agent.id)

    def _exec_status_cmd(self, status_cmd, response):
        agent = dao.agent_with_id(status_cmd.agent_id)

        action = self._ami_client.db_get('xivo/agents', agent.id)
        if action.success:
            response.value = {'logged': True}
        else:
            response.value = {'logged': False}
