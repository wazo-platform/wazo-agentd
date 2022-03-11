# Copyright 2013-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import re

AGENT_NUMBER_REGEX = re.compile(r'^\d+$')


def format_agent_member_name(agent_number):
    return 'Agent/{0}'.format(agent_number)


def format_agent_skills(agent_id):
    return 'agent-{0}'.format(agent_id)


def is_valid_agent_number(agent_number):
    return AGENT_NUMBER_REGEX.match(agent_number)
