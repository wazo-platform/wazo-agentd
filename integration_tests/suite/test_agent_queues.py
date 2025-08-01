# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, contains_inanyorder, has_entries, has_length, is_

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
        assert_that(queues, has_entries(total=0, filtered=0, items=has_length(0)))

        with self.database.queries() as queries:
            queries.associate_queue_agent(queue1['id'], agent['id'])
            queries.associate_queue_agent(queue2['id'], agent['id'])

        queues = self.agentd.agents.list_user_queues()

        assert_that(
            queues,
            has_entries(
                total=2,
                filtered=2,
                items=contains_inanyorder(
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
        assert_that(queues, has_entries(total=0, filtered=0, items=has_length(0)))

        with self.database.queries() as queries:
            queries.associate_queue_agent(queue4['id'], agent['id'])
            queries.associate_queue_agent(queue5['id'], agent['id'])

        queues = self.agentd.agents.list_queues(agent['id'])

        assert_that(
            queues,
            has_entries(
                total=2,
                filtered=2,
                items=contains_inanyorder(
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
            ),
        )

    @fixtures.user_line_extension(exten='1001', context='default', name_line='abcdef')
    @fixtures.agent(number='9999')
    @fixtures.queue(name='queue7', displayname='Q7')
    @fixtures.queue(name='queue8', displayname='Q8')
    @fixtures.queue(name='queue9', displayname='Not a member')
    def test_list_agent_queues_by_number(
        self, user_line_extension, agent, queue7, queue8, queue9
    ):
        with self.database.queries() as queries:
            queries.associate_user_agent(user_line_extension['user_id'], agent['id'])

        queues = self.agentd.agents.list_queues_by_number(agent['number'])
        assert_that(queues, has_entries(total=0, filtered=0, items=has_length(0)))

        with self.database.queries() as queries:
            queries.associate_queue_agent(queue7['id'], agent['id'])
            queries.associate_queue_agent(queue8['id'], agent['id'])

        queues = self.agentd.agents.list_queues_by_number(agent['number'])

        assert_that(
            queues,
            has_entries(
                total=2,
                filtered=2,
                items=contains_inanyorder(
                    has_entries(
                        {
                            'id': queue7['id'],
                            'name': queue7['name'],
                            'display_name': queue7['displayname'],
                        }
                    ),
                    has_entries(
                        {
                            'id': queue8['id'],
                            'name': queue8['name'],
                            'display_name': queue8['displayname'],
                        }
                    ),
                ),
            ),
        )

    @fixtures.user_line_extension(exten='1001', context='default', name_line='abcdef')
    @fixtures.agent(number='1111')
    @fixtures.queue(name='queue10', displayname='A Queue')
    @fixtures.queue(name='queue11', displayname='B Queue')
    @fixtures.queue(name='queue12', displayname='C Queue')
    def test_list_user_queues_ordering(
        self, user_line_extension, agent, queue10, queue11, queue12
    ):
        self.create_user_token(user_line_extension['user_uuid'])

        with self.database.queries() as queries:
            queries.associate_user_agent(user_line_extension['user_id'], agent['id'])
            queries.associate_queue_agent(queue10['id'], agent['id'])
            queries.associate_queue_agent(queue11['id'], agent['id'])
            queries.associate_queue_agent(queue12['id'], agent['id'])

        # Test default ordering (id asc)
        queues = self.agentd.agents.list_user_queues()
        assert_that(queues['items'], has_length(3))
        assert_that(queues['items'][0]['id'], is_(queue10['id']))
        assert_that(queues['items'][1]['id'], is_(queue11['id']))
        assert_that(queues['items'][2]['id'], is_(queue12['id']))

        # Test name ascending
        queues = self.agentd.agents.list_user_queues(order='name', direction='asc')
        assert_that(queues['items'][0]['name'], is_('queue10'))
        assert_that(queues['items'][1]['name'], is_('queue11'))
        assert_that(queues['items'][2]['name'], is_('queue12'))

        # Test name descending
        queues = self.agentd.agents.list_user_queues(order='name', direction='desc')
        assert_that(queues['items'][0]['name'], is_('queue12'))
        assert_that(queues['items'][1]['name'], is_('queue11'))
        assert_that(queues['items'][2]['name'], is_('queue10'))

        # Test display_name ascending
        queues = self.agentd.agents.list_user_queues(
            order='display_name', direction='asc'
        )
        assert_that(queues['items'][0]['display_name'], is_('A Queue'))
        assert_that(queues['items'][1]['display_name'], is_('B Queue'))
        assert_that(queues['items'][2]['display_name'], is_('C Queue'))

        # Test display_name descending
        queues = self.agentd.agents.list_user_queues(
            order='display_name', direction='desc'
        )
        assert_that(queues['items'][0]['display_name'], is_('C Queue'))
        assert_that(queues['items'][1]['display_name'], is_('B Queue'))
        assert_that(queues['items'][2]['display_name'], is_('A Queue'))

    @fixtures.user_line_extension(exten='1001', context='default', name_line='abcdef')
    @fixtures.agent(number='2222')
    @fixtures.queue(name='queue13', displayname='X Queue')
    @fixtures.queue(name='queue14', displayname='Y Queue')
    @fixtures.queue(name='queue15', displayname='Z Queue')
    def test_list_agent_queues_by_id_ordering(
        self, user_line_extension, agent, queue13, queue14, queue15
    ):
        with self.database.queries() as queries:
            queries.associate_user_agent(user_line_extension['user_id'], agent['id'])
            queries.associate_queue_agent(queue13['id'], agent['id'])
            queries.associate_queue_agent(queue14['id'], agent['id'])
            queries.associate_queue_agent(queue15['id'], agent['id'])

        # Test default ordering (id asc)
        queues = self.agentd.agents.list_queues(agent['id'])
        assert_that(queues['items'], has_length(3))
        assert_that(queues['items'][0]['id'], is_(queue13['id']))
        assert_that(queues['items'][1]['id'], is_(queue14['id']))
        assert_that(queues['items'][2]['id'], is_(queue15['id']))

        # Test name descending
        queues = self.agentd.agents.list_queues(
            agent['id'], order='name', direction='desc'
        )
        assert_that(queues['items'][0]['name'], is_('queue15'))
        assert_that(queues['items'][1]['name'], is_('queue14'))
        assert_that(queues['items'][2]['name'], is_('queue13'))

        # Test display_name ascending
        queues = self.agentd.agents.list_queues(
            agent['id'], order='display_name', direction='asc'
        )
        assert_that(queues['items'][0]['display_name'], is_('X Queue'))
        assert_that(queues['items'][1]['display_name'], is_('Y Queue'))
        assert_that(queues['items'][2]['display_name'], is_('Z Queue'))

    @fixtures.user_line_extension(exten='1001', context='default', name_line='abcdef')
    @fixtures.agent(number='3333')
    @fixtures.queue(name='queue16', displayname='First Queue')
    @fixtures.queue(name='queue17', displayname='Second Queue')
    @fixtures.queue(name='queue18', displayname='Third Queue')
    def test_list_agent_queues_by_number_ordering(
        self, user_line_extension, agent, queue16, queue17, queue18
    ):
        with self.database.queries() as queries:
            queries.associate_user_agent(user_line_extension['user_id'], agent['id'])
            queries.associate_queue_agent(queue16['id'], agent['id'])
            queries.associate_queue_agent(queue17['id'], agent['id'])
            queries.associate_queue_agent(queue18['id'], agent['id'])

        # Test default ordering (id asc)
        queues = self.agentd.agents.list_queues_by_number(agent['number'])
        assert_that(queues['items'], has_length(3))
        assert_that(queues['items'][0]['id'], is_(queue16['id']))
        assert_that(queues['items'][1]['id'], is_(queue17['id']))
        assert_that(queues['items'][2]['id'], is_(queue18['id']))

        # Test name ascending
        queues = self.agentd.agents.list_queues_by_number(
            agent['number'], order='name', direction='asc'
        )
        assert_that(queues['items'][0]['name'], is_('queue16'))
        assert_that(queues['items'][1]['name'], is_('queue17'))
        assert_that(queues['items'][2]['name'], is_('queue18'))

        # Test display_name descending
        queues = self.agentd.agents.list_queues_by_number(
            agent['number'], order='display_name', direction='desc'
        )
        assert_that(queues['items'][0]['display_name'], is_('Third Queue'))
        assert_that(queues['items'][1]['display_name'], is_('Second Queue'))
        assert_that(queues['items'][2]['display_name'], is_('First Queue'))
