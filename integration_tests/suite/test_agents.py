# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, calling, has_properties

from wazo_agentd_client.error import AgentdClientError, UNAUTHORIZED
from xivo_test_helpers.hamcrest.raises import raises

from .helpers.base import BaseIntegrationTest, UNKNOWN_UUID


class TestAgents(BaseIntegrationTest):

    asset = 'base'

    def test_authentication(self):
        agentd_client = self.make_agentd(token=UNKNOWN_UUID)
        assert_that(
            calling(agentd_client.agents.get_agent_statuses),
            raises(AgentdClientError, has_properties(error=UNAUTHORIZED)),
        )
