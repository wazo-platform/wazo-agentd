# Copyright (C) 2012-2014 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_agent.ami.actions.common.action import BaseAction


def DBPutAction(family, key, value):
    return BaseAction('DBPut', [
        ('Family', family),
        ('Key', key),
        ('Val', value),
    ])
