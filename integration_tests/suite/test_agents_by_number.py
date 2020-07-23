# Copyright 2019-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, contains, has_entries
from xivo_test_helpers import until

from .helpers.base import BaseIntegrationTest
from .helpers import fixtures


class TestAgentsByNumber(BaseIntegrationTest):

    asset = 'base'

    @fixtures.user_line_extension(exten='1001', context='default')
    @fixtures.agent(number='1001')
    def test_event_on_login(self, user_line_extension, agent):
        event_accumulator = self.bus.accumulator('status.agent')

        self.agentd.agents.login_agent_by_number(
            agent['number'],
            user_line_extension['exten'],
            user_line_extension['context'],
        )

        def event_received():
            events = event_accumulator.accumulate()
            assert_that(
                events,
                contains(
                    has_entries(
                        data=has_entries(agent_id=agent['id'], status='logged_in')
                    )
                ),
            )

        until.assert_(event_received, tries=3)
