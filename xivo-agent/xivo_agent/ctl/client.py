# -*- coding: UTF-8 -*-

# Copyright (C) 2012-2013  Avencall
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
from xivo_agent.ctl import commands
from xivo_agent.ctl.amqp_transport_client import AMQPTransportClient
from xivo_agent.ctl.marshaler import Marshaler
from xivo_agent.exception import AgentClientError

_AgentStatus = namedtuple('_AgentStatus', ['id', 'number', 'extension', 'context', 'logged'])


class AgentClient(object):

    DEFAULT_HOST = 'localhost'
    DEFAULT_PORT = 5672

    def __init__(self):
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
        self._hostname = hostname
        self._port = port

        self._transport = self._setup_transport()

    def _setup_transport(self):
        transport = AMQPTransportClient.create_and_connect(self._hostname, self._port)
        return transport

    def add_agent_to_queue(self, agent_id, queue_id):
        cmd = commands.AddToQueueCommand(agent_id, queue_id)
        self._execute_command(cmd)

    def remove_agent_from_queue(self, agent_id, queue_id):
        cmd = commands.RemoveFromQueueCommand(agent_id, queue_id)
        self._execute_command(cmd)

    def login_agent(self, agent_id, extension, context):
        cmd = commands.LoginCommand(extension, context).by_id(agent_id)
        self._execute_command(cmd)

    def login_agent_by_number(self, agent_number, extension, context):
        cmd = commands.LoginCommand(extension, context).by_number(agent_number)
        self._execute_command(cmd)

    def logoff_agent(self, agent_id):
        cmd = commands.LogoffCommand().by_id(agent_id)
        self._execute_command(cmd)

    def logoff_agent_by_number(self, agent_number):
        cmd = commands.LogoffCommand().by_number(agent_number)
        self._execute_command(cmd)

    def logoff_all_agents(self):
        cmd = commands.LogoffAllCommand()
        self._execute_command(cmd)

    def get_agent_status(self, agent_id):
        cmd = commands.StatusCommand().by_id(agent_id)
        status = self._execute_command(cmd)
        return self._convert_agent_status(status)

    def get_agent_status_by_number(self, agent_number):
        cmd = commands.StatusCommand().by_number(agent_number)
        status = self._execute_command(cmd)
        return self._convert_agent_status(status)

    def get_agent_statuses(self):
        cmd = commands.StatusesCommand()
        statuses = self._execute_command(cmd)
        return [self._convert_agent_status(status) for status in statuses]

    def on_agent_updated(self, agent_id):
        cmd = commands.OnAgentUpdatedCommand(agent_id)
        self._execute_command_no_response(cmd)

    def on_agent_deleted(self, agent_id):
        cmd = commands.OnAgentDeletedCommand(agent_id)
        self._execute_command_no_response(cmd)

    def on_queue_added(self, queue_id):
        cmd = commands.OnQueueAddedCommand(queue_id)
        self._execute_command_no_response(cmd)

    def on_queue_updated(self, queue_id):
        cmd = commands.OnQueueUpdatedCommand(queue_id)
        self._execute_command_no_response(cmd)

    def on_queue_deleted(self, queue_id):
        cmd = commands.OnQueueDeletedCommand(queue_id)
        self._execute_command_no_response(cmd)

    def ping(self):
        cmd = commands.PingCommand()
        return self._execute_command(cmd)

    def _execute_command(self, cmd):
        request = self._marshaler.marshal_command(cmd)
        raw_response = self._transport.rpc_call(request)
        response = self._marshaler.unmarshal_response(raw_response)
        if response.error is not None:
            raise AgentClientError(response.error)
        return response.value

    def _execute_command_no_response(self, cmd):
        request = self._marshaler.marshal_command(cmd)
        self._transport.send(request)

    def _convert_agent_status(self, status):
        return _AgentStatus(status['id'], status['number'], status['extension'],
                            status['context'], status['logged'])
