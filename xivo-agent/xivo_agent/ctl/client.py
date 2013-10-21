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
from xivo_bus.ressource.agent import command
from xivo_agent.ctl.marshaler import Marshaler
from xivo_agent.exception import AgentClientError
from xivo_bus.ctl.amqp_transport_client import AMQPTransportClient

_AgentStatus = namedtuple('_AgentStatus', ['id', 'number', 'extension', 'context', 'logged'])


class AgentClient(object):

    DEFAULT_HOST = 'localhost'
    DEFAULT_PORT = 5672
    _QUEUE_NAME = 'xivo_agent'

    def __init__(self, fetch_response=True):
        self._fetch_response = fetch_response
        self._transport = None
        self._marshaler = Marshaler()

    def close(self):
        if self._transport is None:
            return

        self._transport.close()
        self._transport = None

    def connect(self, hostname=DEFAULT_HOST, port=DEFAULT_PORT):
        if self._transport is not None:
            raise Exception('already connected')

        self._transport = self._new_transport(hostname, port)

    def _new_transport(self, hostname, port):
        return AMQPTransportClient.create_and_connect(hostname, port, self._QUEUE_NAME)

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

    def ping(self):
        cmd = command.PingCommand()
        return self._execute_command(cmd)

    def _execute_command(self, cmd):
        request = self._marshaler.marshal_command(cmd)
        if self._fetch_response:
            return self._execute_request_fetch_response(request)
        else:
            return self._execute_request_no_fetch_response(request)

    def _execute_request_fetch_response(self, request):
        raw_response = self._transport.rpc_call(request)
        response = self._marshaler.unmarshal_response(raw_response)
        if response.error is not None:
            raise AgentClientError(response.error)
        return response.value

    def _execute_request_no_fetch_response(self, request):
        self._transport.send(request)

    def _convert_agent_status(self, status):
        return _AgentStatus(status['id'], status['number'], status['extension'],
                            status['context'], status['logged'])
