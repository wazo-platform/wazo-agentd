# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, contains_inanyorder, has_entries, has_length

from .helpers import fixtures
from .helpers.base import BaseIntegrationTest


class TestAgentQueues(BaseIntegrationTest):
    asset = 'base'

    @fixtures.user_line_extension(exten='1001', context='default', name_line='abcdef')
    @fixtures.agent(number='1234')
    @fixtures.queue(name='queue1', displayname='Q1')
    @fixtures.queue(name='queue2', displayname='Q2')
    @fixtures.queue(name='queue3', displayname='Not a member')
    def test_list_user_queues(self, user_line_extension, agent, queue1, queue2, queue3):
        self.create_user_token(user_line_extension['user_uuid'])

        with self.database.queries() as queries:
            queries.associate_user_agent(user_line_extension['user_id'], agent['id'])

        queues = self.agentd.agents.list_user_queues()
        assert_that(queues, has_length(0))

        with self.database.queries() as queries:
            queries.associate_queue_agent(queue1['id'], agent['id'])
            queries.associate_queue_agent(queue2['id'], agent['id'])

        queues = self.agentd.agents.list_user_queues()

        assert_that(
            queues,
            contains_inanyorder(
                has_entries(
                    {
                        'id': queue1['id'],
                        'name': queue1['name'],
                        'display_name': queue1['displayname'],
                    }
                ),
                has_entries(
                    {
                        'id': queue2['id'],
                        'name': queue2['name'],
                        'display_name': queue2['displayname'],
                    }
                ),
            ),
        )

    @fixtures.user_line_extension(exten='1001', context='default', name_line='abcdef')
    @fixtures.agent(number='5678')
    @fixtures.queue(name='queue4', displayname='Q4')
    @fixtures.queue(name='queue5', displayname='Q5')
    @fixtures.queue(name='queue6', displayname='Not a member')
    def test_list_agent_queues_by_id(
        self, user_line_extension, agent, queue4, queue5, queue6
    ):
        with self.database.queries() as queries:
            queries.associate_user_agent(user_line_extension['user_id'], agent['id'])

        queues = self.agentd.agents.list_queues(agent['id'])
        assert_that(queues, has_length(0))

        with self.database.queries() as queries:
            queries.associate_queue_agent(queue4['id'], agent['id'])
            queries.associate_queue_agent(queue5['id'], agent['id'])

        queues = self.agentd.agents.list_queues(agent['id'])

        assert_that(
            queues,
            contains_inanyorder(
                has_entries(
                    {
                        'id': queue4['id'],
                        'name': queue4['name'],
                        'display_name': queue4['displayname'],
                    }
                ),
                has_entries(
                    {
                        'id': queue5['id'],
                        'name': queue5['name'],
                        'display_name': queue5['displayname'],
                    }
                ),
            ),
        )
