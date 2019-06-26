# Copyright 2012-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_agentd.ami.actions.common.action import BaseAction


def LoginAction(username, password):
    return BaseAction('Login', [
        ('Username', username),
        ('Secret', password),
    ])
