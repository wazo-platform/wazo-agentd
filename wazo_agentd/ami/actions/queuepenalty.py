# Copyright 2013-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_agentd.ami.actions.common.action import BaseAction


def QueuePenaltyAction(interface, penalty, queue=None):
    return BaseAction(
        'QueuePenalty',
        [('Interface', interface), ('Penalty', penalty), ('Queue', queue)],
    )
