# -*- coding: utf-8 -*-
# Copyright 2012-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_agent.ami.actions.common.action import BaseAction


def QueueAddAction(queue, interface, member_name=None, state_interface=None, penalty=None, skills=None):
    # TODO clean after pjsip migration
    if state_interface.startswith('SIP/'):
        state_interface = state_interface.replace('SIP/', 'PJSIP/')

    return BaseAction('QueueAdd', [
        ('Queue', queue),
        ('Interface', interface),
        ('MemberName', member_name),
        ('StateInterface', state_interface),
        ('Penalty', penalty),
        ('Skills', skills),
    ])
