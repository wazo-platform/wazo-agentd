# -*- coding: UTF-8 -*-

from xivo_agent.ami.actions.common.action import BaseAction


def QueueRemoveAction(queue, interface):
    return BaseAction('QueueRemove', [
        ('Queue', queue),
        ('Interface', interface),
    ])
