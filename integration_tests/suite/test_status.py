# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


from hamcrest import (
    assert_that,
    has_properties,
)

from .helpers.base import BaseIntegrationTest
from .helpers import fixtures


class TestAgentsStatus(BaseIntegrationTest):

    asset = 'base'

    @fixtures.user_line_extension(exten='1001', context='default', name_line='abcdef')
    @fixtures.agent(number='1234')
    def test_agent_status(self, user_line_extension, agent):

        self.agentd.agents.login_agent(
            agent['id'],
            user_line_extension['exten'],
            user_line_extension['context'],
        )

        status = self.agentd.status.get_agent_status(agent['id'])
        assert_that(
            status,
            has_properties(
                {
                    'id': agent['id'],
                    'logged': True,
                    'context': 'default',
                    'extension': '1001',
                    'number': '1234',
                    'state_interface': 'PJSIP/abcdef',
                }
            ),
        )
