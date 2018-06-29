# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_agent.ami.actions.common.action import BaseAction


def QueuePauseAction(interface, paused, reason=None, queue=None):
    return BaseAction('QueuePause', [
        ('Interface', interface),
        ('Paused', paused),
        ('Queue', queue),
        ('Reason', reason),
    ])
