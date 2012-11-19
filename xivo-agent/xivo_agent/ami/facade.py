# -*- coding: UTF-8 -*-

from xivo_agent.ami import actions, client


class FacadeAMIClient(object):

    _ACTIONS = [
        ('db_del', actions.DBDelAction),
        ('db_get', actions.DBGetAction),
        ('db_put', actions.DBPutAction),
        ('queue_add', actions.QueueAddAction),
        ('queue_remove', actions.QueueRemoveAction),
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
