# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+


def format_agent_member_name(agent_number):
    return 'Agent/{0}'.format(agent_number)


def format_agent_skills(agent_id):
    return 'agent-{0}'.format(agent_id)
