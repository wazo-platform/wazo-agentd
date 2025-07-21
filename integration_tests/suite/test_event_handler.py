# Copyright 2019-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import time

import wazo_agentd_client.error
from hamcrest import assert_that, calling, is_, raises
from wazo_test_helpers import until

from .helpers import fixtures
from .helpers.base import BaseIntegrationTest


class TestEventHandler(BaseIntegrationTest):
    asset = 'base'

    @fixtures.user_line_extension(exten='1001', context='default')
    @fixtures.agent(number='1001')
    @fixtures.queue()
    def test_delete_queue_event(self, user_line_extension, agent, queue):
        with self.database.queries() as queries:
            queries.associate_user_agent(user_line_extension['user_id'], agent['id'])
            queries.associate_queue_agent(queue['id'], agent['id'])
            queries.insert_agent_membership_status(queue['id'], agent['id'])

        def test_on_msg_received():
            self.bus.send_delete_queue_event(queue['id'])
            time.sleep(0.5)

            with self.database.queries() as queries:
                membership = queries.get_agent_membership_status(
                    queue['id'], agent['id']
                )
                assert_that(membership, is_(None))

        until.assert_(test_on_msg_received, tries=10)

    @fixtures.agent(number='1001')
    def test_on_agent_deleted(self, agent):
        with self.database.queries() as queries:
            with queries.inserter() as inserter:
                inserter.add_agent_login_status(
                    agent_id=agent['id'], agent_number=agent['number']
                )

        def check_agent_status():
            assert_that(
                calling(self.agentd.agents.get_agent_status).with_args(agent['id']),
                raises(wazo_agentd_client.error.AgentdClientError),
            )
            with self.database.queries() as queries:
                status = queries.get_agent_login_status_by_id(agent['id'])
                assert_that(status, is_(None))

        with self.database.queries() as queries:
            queries.delete_only_agent(agent['id'])
        self.bus.send_agent_deleted_event(agent['id'])
        until.assert_(check_agent_status, tries=10)
