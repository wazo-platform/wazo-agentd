# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, is_
from wazo_test_helpers import until

from .helpers.base import BaseIntegrationTest
from .helpers import fixtures


class TestLogoutAgentHandler(BaseIntegrationTest):
    asset = 'base'

    @fixtures.user_line_extension(exten='1001', context='default')
    @fixtures.agent(number='1001')
    def test_logout_agent(self, user_line_extension, agent):
        with self.database.queries() as queries:
            queries.associate_user_agent(user_line_extension['user_id'], agent['id'])

        self.agentd.agents.login_agent(
            agent['id'],
            user_line_extension['exten'],
            user_line_extension['context'],
        )

        status = self.agentd.agents.get_agent_status(agent['id'])
        assert_that(status.logged, is_(True))

        self.bus.publish(
            {
                'data': {
                    'Device': f'PJSIP/{user_line_extension["device_name"]}',
                    'State': 'UNAVAILABLE'
                },
                'name': 'DeviceStateChange',
            },
            headers={'name': 'DeviceStateChange'},
        )

        def test_on_agent_logged_out():
            status = self.agentd.agents.get_agent_status(agent['id'])
            assert_that(status.logged, is_(False))

        until.assert_(test_on_agent_logged_out, tries=10)
