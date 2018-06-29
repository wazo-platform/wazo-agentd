# -*- coding: utf-8 -*-
# Copyright (C) 2012-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_agent.ami.actions.common.action import BaseAction


def UserEventAction(user_event, headers):
    params = [('UserEvent', user_event)]
    params.extend(headers)
    return BaseAction('UserEvent', params)
