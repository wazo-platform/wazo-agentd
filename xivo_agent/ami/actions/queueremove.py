# -*- coding: utf-8 -*-
# Copyright (C) 2012-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_agent.ami.actions.common.action import BaseAction


def QueueRemoveAction(queue, interface):
    return BaseAction('QueueRemove', [
        ('Queue', queue),
        ('Interface', interface),
    ])
