# -*- coding: UTF-8 -*-

from xivo_agent.ami.actions.common.action import BaseAction


def DBDelAction(family, key):
    return BaseAction('DBDel', [
        ('Family', family),
        ('Key', key),
    ])
