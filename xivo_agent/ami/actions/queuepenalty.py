# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_agent.ami.actions.common.action import BaseAction


def QueuePenaltyAction(interface, penalty, queue=None):
    return BaseAction('QueuePenalty', [
        ('Interface', interface),
        ('Penalty', penalty),
        ('Queue', queue),
    ])
