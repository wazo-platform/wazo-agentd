# Copyright 2012-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_agent.ami import actions, client


class FacadeAMIClient:

    _ACTIONS = [
        ('db_del', actions.DBDelAction),
        ('db_get', actions.DBGetAction),
        ('db_put', actions.DBPutAction),
        ('queue_add', actions.QueueAddAction),
        ('queue_pause', actions.QueuePauseAction),
        ('queue_penalty', actions.QueuePenaltyAction),
        ('queue_remove', actions.QueueRemoveAction),
        ('user_event', actions.UserEventAction),
    ]
    _PORT = 5038

    def __init__(self, hostname, username, password):
        self._ami_client = client.ReconnectingAMIClient(hostname, self._PORT, self._login)
        self._username = username
        self._password = password
        self._add_action_functions()

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
