# -*- coding: UTF-8 -*-

import logging
from xivo_agent import dao
from xivo_agent.ctl import commands

logger = logging.getLogger(__name__)


class AgentService(object):

    def __init__(self, ami_client, ctl_server):
        self._ami_client = ami_client
        self._ctl_server = ctl_server

    def init(self):
        self._ctl_server.add_command(commands.LoginCommand, self._exec_login_cmd)
        self._ctl_server.add_command(commands.LogoffCommand, self._exec_logoff_cmd)
        self._ctl_server.add_command(commands.StatusCommand, self._exec_status_cmd)

    def run(self):
        while True:
            self._ctl_server.process_next_command()

    def _exec_login_cmd(self, login_cmd, response):
        # TODO don't log the agent if he's already logged
        # TODO don't log 2 agents on the same interface (this would be easier if
        #      it was in postgres than ast db)
        agent = dao.agent_with_number(login_cmd.agent_number)

        member_name = 'Agent/%s' % agent.id

        self._ami_client.db_put('xivo/agents', agent.id, login_cmd.interface)

        for queue in agent.queues:
            action = self._ami_client.queue_add(queue.name, login_cmd.interface, member_name)
            if not action.success:
                logger.warning('Failure to add interface %r to queue %r', login_cmd.interface, queue.name)

    def _exec_logoff_cmd(self, logoff_cmd, response):
        agent = dao.agent_with_number(logoff_cmd.agent_number)

        action = self._ami_client.db_get('xivo/agents', agent.id)
        if action.success:
            # agent is logged
            interface = action.val
            for queue in agent.queues:
                action = self._ami_client.queue_remove(queue.name, interface)
            self._ami_client.db_del('xivo/agents', agent.id)

    def _exec_status_cmd(self, status_cmd, response):
        agent = dao.agent_with_number(status_cmd.agent_number)

        action = self._ami_client.db_get('xivo/agents', agent.id)
        if action.success:
            response.value = {'logged': True}
        else:
            response.value = {'logged': False}
