# -*- coding: UTF-8 -*-

from xivo_agent.ami.actions.common.action import BaseAction


def LoginAction(username, password):
    return BaseAction('Login', [
        ('Username', username),
        ('Secret', password),
    ])
