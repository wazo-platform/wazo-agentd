# Copyright 2012-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_agentd.ami.actions.common.action import BaseAction


def UserEventAction(user_event, headers):
    params = [('UserEvent', user_event)]
    params.extend(headers)
    return BaseAction('UserEvent', params)
