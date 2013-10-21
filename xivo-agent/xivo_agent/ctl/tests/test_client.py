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

import unittest
from mock import Mock, patch
from xivo_bus.ctl.amqp_transport_client import AMQPTransportClient
from xivo_bus.ctl.marshaler import Marshaler
from xivo_agent.ctl.client import AgentClient, _AgentStatus


class TestAgentClient(unittest.TestCase):

    def setUp(self):
        self.marshaler = Mock(Marshaler)
        self.transport = Mock(AMQPTransportClient)
        self.agent_client = AgentClient()
        self._queue_name = self.agent_client._QUEUE_NAME
        self.agent_client._marshaler = self.marshaler
        self.agent_client._transport = self.transport

    def test_execute_command_with_fetch_response(self):
        command = Mock()
        request = Mock()
        raw_response = Mock()
        response = Mock()
        response.error = None
        self.marshaler.marshal_command.return_value = request
        self.transport.rpc_call.return_value = raw_response
        self.marshaler.unmarshal_response.return_value = response

        self.agent_client._fetch_response = True
        result = self.agent_client._execute_command(command)

        self.marshaler.marshal_command.assert_called_once_with(command)
        self.transport.rpc_call.assert_called_once_with(request)
        self.assertEqual(result, response.value)

    def test_execute_command_without_fetch_response(self):
        command = Mock()
        request = Mock()
        self.marshaler.marshal_command.return_value = request

        self.agent_client._fetch_response = False
        self.agent_client._execute_command(command)

        self.marshaler.marshal_command.assert_called_once_with(command)
        self.transport.send.assert_called_once_with(request)

    @patch('xivo_bus.ressource.agent.command.AddToQueueCommand')
    def test_add_agent_to_queue(self, AddToQueueCommand):
        agent_id = 42
        queue_id = 1
        command = Mock()
        AddToQueueCommand.return_value = command
        self.agent_client._execute_command = Mock()

        self.agent_client.add_agent_to_queue(agent_id, queue_id)

        AddToQueueCommand.assert_called_once_with(agent_id, queue_id)
        self.agent_client._execute_command.assert_called_once_with(command)

    @patch('xivo_bus.ressource.agent.command.RemoveFromQueueCommand')
    def test_remove_agent_from_queue(self, RemoveFromQueueCommand):
        agent_id = 42
        queue_id = 1
        command = Mock()
        RemoveFromQueueCommand.return_value = command
        self.agent_client._execute_command = Mock()

        self.agent_client.remove_agent_from_queue(agent_id, queue_id)

        RemoveFromQueueCommand.assert_called_once_with(agent_id, queue_id)
        self.agent_client._execute_command.assert_called_once_with(command)

    @patch('xivo_bus.ressource.agent.command.LoginByIDCommand')
    def test_login_agent(self, LoginByIDCommand):
        agent_id = 42
        extension = '1001'
        context = 'default'
        command = Mock()

        LoginByIDCommand.return_value = command
        self.agent_client._execute_command = Mock()

        self.agent_client.login_agent(agent_id, extension, context)

        LoginByIDCommand.assert_called_once_with(agent_id, extension, context)
        self.agent_client._execute_command.assert_called_once_with(command)

    @patch('xivo_bus.ressource.agent.command.LoginByNumberCommand')
    def test_login_agent_by_number(self, LoginByNumberCommand):
        agent_number = '1'
        extension = '1001'
        context = 'default'
        command = Mock()

        LoginByNumberCommand.return_value = command
        self.agent_client._execute_command = Mock()

        self.agent_client.login_agent_by_number(agent_number, extension, context)

        LoginByNumberCommand.assert_called_once_with(agent_number, extension, context)
        self.agent_client._execute_command.assert_called_once_with(command)

    @patch('xivo_bus.ressource.agent.command.LogoffByIDCommand')
    def test_logoff_agent(self, LogoffByIDCommand):
        agent_id = 42
        command = Mock()

        LogoffByIDCommand.return_value = command
        self.agent_client._execute_command = Mock()

        self.agent_client.logoff_agent(agent_id)

        LogoffByIDCommand.assert_called_once_with(agent_id)
        self.agent_client._execute_command.assert_called_once_with(command)

    @patch('xivo_bus.ressource.agent.command.LogoffByNumberCommand')
    def test_logoff_agent_by_number(self, LogoffByNumberCommand):
        agent_number = '1000'
        command = Mock()

        LogoffByNumberCommand.return_value = command
        self.agent_client._execute_command = Mock()

        self.agent_client.logoff_agent_by_number(agent_number)

        LogoffByNumberCommand.assert_called_once_with(agent_number)
        self.agent_client._execute_command.assert_called_once_with(command)

    @patch('xivo_bus.ressource.agent.command.LogoffAllCommand')
    def test_logoff_all_agents(self, LogoffAllCommand):
        command = Mock()

        LogoffAllCommand.return_value = command
        self.agent_client._execute_command = Mock()

        self.agent_client.logoff_all_agents()

        LogoffAllCommand.assert_called_once_with()
        self.agent_client._execute_command.assert_called_once_with(command)

    @patch('xivo_bus.ressource.agent.command.RelogAllCommand')
    def test_relog_all_agents(self, RelogAllCommand):
        command = Mock()

        RelogAllCommand.return_value = command
        self.agent_client._execute_command = Mock()

        self.agent_client.relog_all_agents()

        RelogAllCommand.assert_called_once_with()
        self.agent_client._execute_command.assert_called_once_with(command)

    @patch('xivo_bus.ressource.agent.command.StatusByIDCommand')
    def test_get_agent_status(self, StatusByIDCommand):
        agent_id = 42
        agent = {
            'id': agent_id,
            'number': '1001',
            'extension': '9001',
            'context': 'default',
            'logged': True,
        }
        command = Mock()
        StatusByIDCommand.return_value = command

        execute_command = Mock()
        execute_command.return_value = agent
        self.agent_client._execute_command = execute_command

        status = self.agent_client.get_agent_status(agent_id)

        self.assertTrue(isinstance(status, _AgentStatus))
        self.assertEquals(status.id, agent['id'])
        self.assertEquals(status.number, agent['number'])
        self.assertEquals(status.extension, agent['extension'])
        self.assertEquals(status.context, agent['context'])
        self.assertEquals(status.logged, agent['logged'])

        StatusByIDCommand.assert_called_once_with(agent_id)
        self.agent_client._execute_command.assert_called_once_with(command)

    @patch('xivo_bus.ressource.agent.command.StatusByNumberCommand')
    def test_get_agent_status_by_number(self, StatusByNumberCommand):
        agent = {
            'id': 1,
            'number': '1001',
            'extension': '9001',
            'context': 'default',
            'logged': True,
        }

        agent_number = '1001'

        command = Mock()
        StatusByNumberCommand.return_value = command

        execute_command = Mock()
        execute_command.return_value = agent
        self.agent_client._execute_command = execute_command

        status = self.agent_client.get_agent_status_by_number(agent_number)

        self.assertTrue(isinstance(status, _AgentStatus))
        self.assertEquals(status.id, agent['id'])
        self.assertEquals(status.number, agent['number'])
        self.assertEquals(status.extension, agent['extension'])
        self.assertEquals(status.context, agent['context'])
        self.assertEquals(status.logged, agent['logged'])

        StatusByNumberCommand.assert_called_once_with(agent_number)
        self.agent_client._execute_command.assert_called_once_with(command)

    @patch('xivo_bus.ressource.agent.command.StatusesCommand')
    def test_get_agent_statuses(self, StatusesCommand):
        agent1 = {
            'id': 1,
            'number': '1001',
            'extension': '9001',
            'context': 'default',
            'logged': True,
        }

        agent2 = {
            'id': 2,
            'number': '1002',
            'extension': None,
            'context': None,
            'logged': False,
        }

        command = Mock()
        StatusesCommand.return_value = command

        execute_command = Mock()
        execute_command.return_value = [agent1, agent2]
        self.agent_client._execute_command = execute_command

        statuses = self.agent_client.get_agent_statuses()

        self.assertTrue(isinstance(statuses[0], _AgentStatus))
        self.assertEquals(statuses[0].id, agent1['id'])
        self.assertEquals(statuses[0].number, agent1['number'])
        self.assertEquals(statuses[0].extension, agent1['extension'])
        self.assertEquals(statuses[0].context, agent1['context'])
        self.assertEquals(statuses[0].logged, agent1['logged'])

        self.assertTrue(isinstance(statuses[1], _AgentStatus))
        self.assertEquals(statuses[1].id, agent2['id'])
        self.assertEquals(statuses[1].number, agent2['number'])
        self.assertEquals(statuses[1].extension, agent2['extension'])
        self.assertEquals(statuses[1].context, agent2['context'])
        self.assertEquals(statuses[1].logged, agent2['logged'])

        StatusesCommand.assert_called_once_with()
        self.agent_client._execute_command.assert_called_once_with(command)

    @patch('xivo_bus.ressource.agent.command.OnAgentUpdatedCommand')
    def test_on_agent_updated_command(self, OnAgentUpdatedCommand):
        agent_id = 42
        self.agent_client._execute_command = Mock()
        command = Mock()
        OnAgentUpdatedCommand.return_value = command

        self.agent_client.on_agent_updated(agent_id)

        OnAgentUpdatedCommand.assert_called_once_with(agent_id)
        self.agent_client._execute_command.assert_called_once_with(command)

    @patch('xivo_bus.ressource.agent.command.OnAgentDeletedCommand')
    def test_on_agent_deleted_command(self, OnAgentDeletedCommand):
        agent_id = 42
        self.agent_client._execute_command = Mock()
        command = Mock()
        OnAgentDeletedCommand.return_value = command

        self.agent_client.on_agent_deleted(agent_id)

        OnAgentDeletedCommand.assert_called_once_with(agent_id)
        self.agent_client._execute_command.assert_called_once_with(command)

    @patch('xivo_bus.ressource.agent.command.OnQueueAddedCommand')
    def test_on_queue_added_command(self, OnQueueAddedCommand):
        queue_id = 42
        self.agent_client._execute_command = Mock()
        command = Mock()
        OnQueueAddedCommand.return_value = command

        self.agent_client.on_queue_added(queue_id)

        OnQueueAddedCommand.assert_called_once_with(queue_id)
        self.agent_client._execute_command.assert_called_once_with(command)

    @patch('xivo_bus.ressource.agent.command.OnQueueUpdatedCommand')
    def test_on_queue_updated_command(self, OnQueueUpdatedCommand):
        queue_id = 42
        self.agent_client._execute_command = Mock()
        command = Mock()
        OnQueueUpdatedCommand.return_value = command

        self.agent_client.on_queue_updated(queue_id)

        OnQueueUpdatedCommand.assert_called_once_with(queue_id)
        self.agent_client._execute_command.assert_called_once_with(command)

    @patch('xivo_bus.ressource.agent.command.OnQueueDeletedCommand')
    def test_on_queue_deleted_command(self, OnQueueDeletedCommand):
        queue_id = 42
        self.agent_client._execute_command = Mock()
        command = Mock()
        OnQueueDeletedCommand.return_value = command

        self.agent_client.on_queue_deleted(queue_id)

        OnQueueDeletedCommand.assert_called_once_with(queue_id)
        self.agent_client._execute_command.assert_called_once_with(command)

    @patch('xivo_bus.ressource.xivo.command.PingCommand')
    def test_ping(self, PingCommand):
        command = Mock()

        PingCommand.return_value = command
        self.agent_client._execute_command = Mock()

        self.agent_client.ping()

        PingCommand.assert_called_once_with()
        self.agent_client._execute_command.assert_called_once_with(command)
