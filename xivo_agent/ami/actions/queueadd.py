# -*- coding: utf-8 -*-
# Copyright (C) 2012-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

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
