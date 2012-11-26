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

    def __init__(self, hostname, username, password):
        self._ami_client = client.AMIClient()
        try:
            self._connect(hostname)
            self._login(username, password)
            self._add_action_functions()
        except Exception:
            self._ami_client.close()
            raise

    def _connect(self, hostname):
        self._ami_client.connect(hostname, 5038)

    def _login(self, username, password):
        action = actions.LoginAction(username, password)
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
        self._ami_client.close()

    def agent_login(self, agent_id, extension, context):
        headers = [
            ('AgentID', agent_id),
            ('Extension', extension),
            ('Context', context)
        ]
        action = actions.UserEventAction('AgentLogin', headers)
        self._ami_client.execute(action)
        return action

    def agent_logoff(self, agent_id):
        action = actions.UserEventAction('AgentLogoff', [('AgentID', agent_id)])
        self._ami_client.execute(action)
        return action
