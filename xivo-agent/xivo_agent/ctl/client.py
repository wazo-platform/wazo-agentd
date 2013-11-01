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

from collections import namedtuple
from xivo_bus.resources.agent import command
from xivo_agent.exception import AgentClientError
from xivo_bus.ctl.client import BusCtlClient
from xivo_bus.ctl.exception import BusCtlClientError

_AgentStatus = namedtuple('_AgentStatus', ['id', 'number', 'extension', 'context', 'logged'])


class AgentClient(BusCtlClient):

    _QUEUE_NAME = 'xivo_agent'

    def add_agent_to_queue(self, agent_id, queue_id):
        cmd = command.AddToQueueCommand(agent_id, queue_id)
        self._execute_command(cmd)

    def remove_agent_from_queue(self, agent_id, queue_id):
        cmd = command.RemoveFromQueueCommand(agent_id, queue_id)
        self._execute_command(cmd)

    def login_agent(self, agent_id, extension, context):
        cmd = command.LoginByIDCommand(agent_id, extension, context)
        self._execute_command(cmd)

    def login_agent_by_number(self, agent_number, extension, context):
        cmd = command.LoginByNumberCommand(agent_number, extension, context)
        self._execute_command(cmd)

    def logoff_agent(self, agent_id):
        cmd = command.LogoffByIDCommand(agent_id)
        self._execute_command(cmd)

    def logoff_agent_by_number(self, agent_number):
        cmd = command.LogoffByNumberCommand(agent_number)
        self._execute_command(cmd)

    def logoff_all_agents(self):
        cmd = command.LogoffAllCommand()
        self._execute_command(cmd)

    def relog_all_agents(self):
        cmd = command.RelogAllCommand()
        self._execute_command(cmd)

    def pause_agent_by_number(self, agent_number):
        cmd = command.PauseByNumberCommand(agent_number)
        self._execute_command(cmd)

    def unpause_agent_by_number(self, agent_number):
        cmd = command.UnpauseByNumberCommand(agent_number)
        self._execute_command(cmd)

    def get_agent_status(self, agent_id):
        cmd = command.StatusByIDCommand(agent_id)
        status = self._execute_command(cmd)
        return self._convert_agent_status(status)

    def get_agent_status_by_number(self, agent_number):
        cmd = command.StatusByNumberCommand(agent_number)
        status = self._execute_command(cmd)
        return self._convert_agent_status(status)

    def get_agent_statuses(self):
        cmd = command.StatusesCommand()
        statuses = self._execute_command(cmd)
        return [self._convert_agent_status(status) for status in statuses]

    def on_agent_updated(self, agent_id):
        cmd = command.OnAgentUpdatedCommand(agent_id)
        self._execute_command(cmd)

    def on_agent_deleted(self, agent_id):
        cmd = command.OnAgentDeletedCommand(agent_id)
        self._execute_command(cmd)

    def on_queue_added(self, queue_id):
        cmd = command.OnQueueAddedCommand(queue_id)
        self._execute_command(cmd)

    def on_queue_updated(self, queue_id):
        cmd = command.OnQueueUpdatedCommand(queue_id)
        self._execute_command(cmd)

    def on_queue_deleted(self, queue_id):
        cmd = command.OnQueueDeletedCommand(queue_id)
        self._execute_command(cmd)

    def _convert_agent_status(self, status):
        return _AgentStatus(status['id'], status['number'], status['extension'],
                            status['context'], status['logged'])

    def _execute_request_fetch_response(self, request):
        try:
            return BusCtlClient._execute_request_fetch_response(self, request)
        except BusCtlClientError as e:
            raise AgentClientError(e.error)
