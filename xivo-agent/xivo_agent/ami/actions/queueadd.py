# -*- coding: UTF-8 -*-

from xivo_agent.ami.actions.common.action import BaseAction


def QueueAddAction(queue, interface, member_name=None):
    return BaseAction('QueueAdd', [
        ('Queue', queue),
        ('Interface', interface),
        ('MemberName', member_name),
    ])
