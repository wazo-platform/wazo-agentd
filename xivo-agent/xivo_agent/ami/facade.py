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

from xivo_agent.ami import actions, client


class FacadeAMIClient(object):

    _ACTIONS = [
        ('db_del', actions.DBDelAction),
        ('db_get', actions.DBGetAction),
        ('db_put', actions.DBPutAction),
        ('queue_add', actions.QueueAddAction),
        ('queue_remove', actions.QueueRemoveAction),
        ('user_event', actions.UserEventAction),
    ]
    _PORT = 5038

    def __init__(self, hostname, username, password):
        self._ami_client = client.AMIClient(hostname, self._PORT)
        self._username = username
        self._password = password
        try:
            self._connect()
            self._login()
            self._add_action_functions()
        except Exception:
            self._ami_client.close()
            raise

    def _connect(self):
        self._ami_client.connect()

    def _login(self):
        action = actions.LoginAction(self._username, self._password)
        self._ami_client.execute(action)
        if not action.success:
            raise Exception('AMI authentication failed')

    def _add_action_functions(self):
        for fun_name, action_factory in self._ACTIONS:
            fun = self._new_action_function(action_factory)
            fun.__name__ = fun_name
            setattr(self, fun_name, fun)

    def _new_action_function(self, action_factory):
        def aux(*args, **kwargs):
            action = action_factory(*args, **kwargs)
            self._ami_client.execute(action)
            return action
        return aux

    def close(self):
        self._ami_client.disconnect()

    def agent_added_to_queue(self, agent_id, agent_number, queue_name):
        headers = [
            ('AgentID', agent_id),
            ('AgentNumber', agent_number),
            ('QueueName', queue_name),
        ]
        action = actions.UserEventAction('AgentAddedToQueue', headers)
        self._ami_client.execute(action)
        return action

    def agent_removed_from_queue(self, agent_id, agent_number, queue_name):
        headers = [
            ('AgentID', agent_id),
            ('AgentNumber', agent_number),
            ('QueueName', queue_name),
        ]
        action = actions.UserEventAction('AgentRemovedFromQueue', headers)
        self._ami_client.execute(action)
        return action

    def agent_login(self, agent_id, agent_number, extension, context):
        headers = [
            ('AgentID', agent_id),
            ('AgentNumber', agent_number),
            ('Extension', extension),
            ('Context', context),
        ]
        action = actions.UserEventAction('AgentLogin', headers)
        self._ami_client.execute(action)
        return action

    def agent_logoff(self, agent_id, agent_number):
        headers = [
            ('AgentID', agent_id),
            ('AgentNumber', agent_number),
        ]
        action = actions.UserEventAction('AgentLogoff', headers)
        self._ami_client.execute(action)
        return action
