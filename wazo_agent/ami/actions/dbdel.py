# Copyright (C) 2012-2014 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_agent.ami.actions.common.action import BaseAction


def DBDelAction(family, key):
    return BaseAction('DBDel', [
        ('Family', family),
        ('Key', key),
    ])
