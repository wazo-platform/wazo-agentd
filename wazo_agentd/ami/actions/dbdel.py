# Copyright 2012-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_agentd.ami.actions.common.action import BaseAction


def DBDelAction(family, key):
    return BaseAction('DBDel', [
        ('Family', family),
        ('Key', key),
    ])
