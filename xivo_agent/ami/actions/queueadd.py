# Copyright 2012-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_agent.ami.actions.common.action import BaseAction


def QueueAddAction(queue, interface, member_name=None, state_interface=None, penalty=None, skills=None):
    return BaseAction('QueueAdd', [
        ('Queue', queue),
        ('Interface', interface),
        ('MemberName', member_name),
        ('StateInterface', state_interface),
        ('Penalty', penalty),
        ('Skills', skills),
    ])
