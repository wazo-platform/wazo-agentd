# -*- coding: UTF-8 -*-

from xivo_agent.ami.actions.common.action import BaseAction


def DBPutAction(family, key, value):
    return BaseAction('DBPut', [
        ('Family', family),
        ('Key', key),
        ('Val', value),
    ])
