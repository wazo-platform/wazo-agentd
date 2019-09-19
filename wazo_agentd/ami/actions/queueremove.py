# Copyright 2012-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_agentd.ami.actions.common.action import BaseAction


def QueueRemoveAction(queue, interface):
    return BaseAction('QueueRemove', [('Queue', queue), ('Interface', interface)])
