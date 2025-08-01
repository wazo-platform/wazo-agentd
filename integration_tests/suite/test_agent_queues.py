# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    calling,
    contains_exactly,
    contains_inanyorder,
    has_entries,
    has_length,
    raises,
)

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
        assert_that(
            queues,
            has_entries(
                items=contains_exactly(
                    has_entries(id=queue10['id']),
                    has_entries(id=queue11['id']),
                    has_entries(id=queue12['id']),
                )
            ),
        )

        # Test name ascending
        queues = self.agentd.agents.list_user_queues(order='name', direction='asc')
        assert_that(
            queues,
            has_entries(
                items=contains_exactly(
                    has_entries(name='queue10'),
                    has_entries(name='queue11'),
                    has_entries(name='queue12'),
                )
            ),
        )

        # Test name descending
        queues = self.agentd.agents.list_user_queues(order='name', direction='desc')
        assert_that(
            queues,
            has_entries(
                items=contains_exactly(
                    has_entries(name='queue12'),
                    has_entries(name='queue11'),
                    has_entries(name='queue10'),
                )
            ),
        )

        # Test display_name ascending
        queues = self.agentd.agents.list_user_queues(
            order='display_name', direction='asc'
        )
        assert_that(
            queues,
            has_entries(
                items=contains_exactly(
                    has_entries(display_name='A Queue'),
                    has_entries(display_name='B Queue'),
                    has_entries(display_name='C Queue'),
                )
            ),
        )

        # Test display_name descending
        queues = self.agentd.agents.list_user_queues(
            order='display_name', direction='desc'
        )
        assert_that(
            queues,
            has_entries(
                items=contains_exactly(
                    has_entries(display_name='C Queue'),
                    has_entries(display_name='B Queue'),
                    has_entries(display_name='A Queue'),
                )
            ),
        )

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
        assert_that(
            queues,
            has_entries(
                items=contains_exactly(
                    has_entries(id=queue13['id']),
                    has_entries(id=queue14['id']),
                    has_entries(id=queue15['id']),
                )
            ),
        )

        # Test name descending
        queues = self.agentd.agents.list_queues(
            agent['id'], order='name', direction='desc'
        )
        assert_that(
            queues,
            has_entries(
                items=contains_exactly(
                    has_entries(name='queue15'),
                    has_entries(name='queue14'),
                    has_entries(name='queue13'),
                )
            ),
        )

        # Test display_name ascending
        queues = self.agentd.agents.list_queues(
            agent['id'], order='display_name', direction='asc'
        )
        assert_that(
            queues,
            has_entries(
                items=contains_exactly(
                    has_entries(display_name='X Queue'),
                    has_entries(display_name='Y Queue'),
                    has_entries(display_name='Z Queue'),
                )
            ),
        )

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
        assert_that(
            queues,
            has_entries(
                items=contains_exactly(
                    has_entries(id=queue16['id']),
                    has_entries(id=queue17['id']),
                    has_entries(id=queue18['id']),
                )
            ),
        )

        # Test name ascending
        queues = self.agentd.agents.list_queues_by_number(
            agent['number'], order='name', direction='asc'
        )
        assert_that(
            queues,
            has_entries(
                items=contains_exactly(
                    has_entries(name='queue16'),
                    has_entries(name='queue17'),
                    has_entries(name='queue18'),
                )
            ),
        )

        # Test display_name descending
        queues = self.agentd.agents.list_queues_by_number(
            agent['number'], order='display_name', direction='desc'
        )
        assert_that(
            queues,
            has_entries(
                items=contains_exactly(
                    has_entries(display_name='Third Queue'),
                    has_entries(display_name='Second Queue'),
                    has_entries(display_name='First Queue'),
                )
            ),
        )

    @fixtures.user_line_extension(exten='1001', context='default', name_line='abcdef')
    @fixtures.agent(number='4444')
    @fixtures.queue(name='queue19', displayname='Queue A')
    @fixtures.queue(name='queue20', displayname='Queue B')
    @fixtures.queue(name='queue21', displayname='Queue C')
    @fixtures.queue(name='queue22', displayname='Queue D')
    @fixtures.queue(name='queue23', displayname='Queue E')
    def test_list_user_queues_pagination(
        self, user_line_extension, agent, queue19, queue20, queue21, queue22, queue23
    ):
        self.create_user_token(user_line_extension['user_uuid'])

        with self.database.queries() as queries:
            queries.associate_user_agent(user_line_extension['user_id'], agent['id'])
            queries.associate_queue_agent(queue19['id'], agent['id'])
            queries.associate_queue_agent(queue20['id'], agent['id'])
            queries.associate_queue_agent(queue21['id'], agent['id'])
            queries.associate_queue_agent(queue22['id'], agent['id'])
            queries.associate_queue_agent(queue23['id'], agent['id'])

        # Test default pagination (limit=100, offset=0)
        queues = self.agentd.agents.list_user_queues()
        assert_that(queues, has_entries(total=5, filtered=5, items=has_length(5)))

        # Test limit=2, offset=0
        queues = self.agentd.agents.list_user_queues(limit=2, offset=0)
        assert_that(
            queues,
            has_entries(
                total=5,
                filtered=2,
                items=contains_exactly(
                    has_entries(id=queue19['id']), has_entries(id=queue20['id'])
                ),
            ),
        )

        # Test limit=2, offset=2
        queues = self.agentd.agents.list_user_queues(limit=2, offset=2)
        assert_that(
            queues,
            has_entries(
                total=5,
                filtered=2,
                items=contains_exactly(
                    has_entries(id=queue21['id']), has_entries(id=queue22['id'])
                ),
            ),
        )

        # Test limit=2, offset=4 (last page)
        queues = self.agentd.agents.list_user_queues(limit=2, offset=4)
        assert_that(
            queues,
            has_entries(
                total=5,
                filtered=1,
                items=contains_exactly(has_entries(id=queue23['id'])),
            ),
        )

        # Test offset beyond total count
        queues = self.agentd.agents.list_user_queues(limit=2, offset=10)
        assert_that(queues, has_entries(total=5, filtered=0, items=has_length(0)))

    @fixtures.user_line_extension(exten='1001', context='default', name_line='abcdef')
    @fixtures.agent(number='5555')
    @fixtures.queue(name='queue24', displayname='Queue X')
    @fixtures.queue(name='queue25', displayname='Queue Y')
    @fixtures.queue(name='queue26', displayname='Queue Z')
    def test_list_agent_queues_by_id_pagination(
        self, user_line_extension, agent, queue24, queue25, queue26
    ):
        with self.database.queries() as queries:
            queries.associate_user_agent(user_line_extension['user_id'], agent['id'])
            queries.associate_queue_agent(queue24['id'], agent['id'])
            queries.associate_queue_agent(queue25['id'], agent['id'])
            queries.associate_queue_agent(queue26['id'], agent['id'])

        # Test limit=1, offset=1
        queues = self.agentd.agents.list_queues(agent['id'], limit=1, offset=1)
        assert_that(
            queues,
            has_entries(
                total=3,
                filtered=1,
                items=contains_exactly(has_entries(id=queue25['id'])),
            ),
        )

        # Test with ordering and pagination
        queues = self.agentd.agents.list_queues(
            agent['id'], order='name', direction='desc', limit=2, offset=0
        )
        assert_that(
            queues,
            has_entries(
                total=3,
                filtered=2,
                items=contains_exactly(
                    has_entries(name='queue26'), has_entries(name='queue25')
                ),
            ),
        )

    @fixtures.user_line_extension(exten='1001', context='default', name_line='abcdef')
    @fixtures.agent(number='6666')
    @fixtures.queue(name='queue27', displayname='First')
    @fixtures.queue(name='queue28', displayname='Second')
    @fixtures.queue(name='queue29', displayname='Third')
    @fixtures.queue(name='queue30', displayname='Fourth')
    def test_list_agent_queues_by_number_pagination(
        self, user_line_extension, agent, queue27, queue28, queue29, queue30
    ):
        with self.database.queries() as queries:
            queries.associate_user_agent(user_line_extension['user_id'], agent['id'])
            queries.associate_queue_agent(queue27['id'], agent['id'])
            queries.associate_queue_agent(queue28['id'], agent['id'])
            queries.associate_queue_agent(queue29['id'], agent['id'])
            queries.associate_queue_agent(queue30['id'], agent['id'])

        # Test limit=3, offset=1
        queues = self.agentd.agents.list_queues_by_number(
            agent['number'], limit=3, offset=1
        )
        assert_that(
            queues,
            has_entries(
                total=4,
                filtered=3,
                items=contains_exactly(
                    has_entries(id=queue28['id']),
                    has_entries(id=queue29['id']),
                    has_entries(id=queue30['id']),
                ),
            ),
        )

        # Test with ordering and pagination
        queues = self.agentd.agents.list_queues_by_number(
            agent['number'], order='display_name', direction='asc', limit=2, offset=2
        )
        assert_that(
            queues,
            has_entries(
                total=4,
                filtered=2,
                items=contains_exactly(
                    has_entries(display_name='Second'),
                    has_entries(display_name='Third'),
                ),
            ),
        )

    @fixtures.user_line_extension(exten='1001', context='default', name_line='abcdef')
    @fixtures.agent(number='7777')
    @fixtures.queue(name='queue31', displayname='Test Queue')
    def test_list_agent_queues_by_id_invalid_params(
        self, user_line_extension, agent, queue31
    ):
        with self.database.queries() as queries:
            queries.associate_user_agent(user_line_extension['user_id'], agent['id'])
            queries.associate_queue_agent(queue31['id'], agent['id'])

        # Test invalid order parameter
        assert_that(
            calling(self.agentd.agents.list_queues).with_args(
                agent['id'], order='invalid'
            ),
            raises(Exception),
        )

        # Test invalid direction parameter
        assert_that(
            calling(self.agentd.agents.list_queues).with_args(
                agent['id'], direction='invalid'
            ),
            raises(Exception),
        )

        # Test negative limit
        assert_that(
            calling(self.agentd.agents.list_queues).with_args(agent['id'], limit=-1),
            raises(Exception),
        )

        # Test negative offset
        assert_that(
            calling(self.agentd.agents.list_queues).with_args(agent['id'], offset=-1),
            raises(Exception),
        )

    @fixtures.user_line_extension(exten='1001', context='default', name_line='abcdef')
    @fixtures.agent(number='8888')
    @fixtures.queue(name='queue32', displayname='Test Queue')
    def test_list_agent_queues_by_number_invalid_params(
        self, user_line_extension, agent, queue32
    ):
        with self.database.queries() as queries:
            queries.associate_user_agent(user_line_extension['user_id'], agent['id'])
            queries.associate_queue_agent(queue32['id'], agent['id'])

        # Test invalid order parameter
        assert_that(
            calling(self.agentd.agents.list_queues_by_number).with_args(
                agent['number'], order='invalid'
            ),
            raises(Exception),
        )

        # Test invalid direction parameter
        assert_that(
            calling(self.agentd.agents.list_queues_by_number).with_args(
                agent['number'], direction='invalid'
            ),
            raises(Exception),
        )

        # Test negative limit
        assert_that(
            calling(self.agentd.agents.list_queues_by_number).with_args(
                agent['number'], limit=-1
            ),
            raises(Exception),
        )

        # Test negative offset
        assert_that(
            calling(self.agentd.agents.list_queues_by_number).with_args(
                agent['number'], offset=-1
            ),
            raises(Exception),
        )

    @fixtures.user_line_extension(exten='1001', context='default', name_line='abcdef')
    @fixtures.agent(number='9999')
    @fixtures.queue(name='queue33', displayname='Test Queue')
    def test_list_user_queues_invalid_params(self, user_line_extension, agent, queue33):
        with self.database.queries() as queries:
            queries.associate_user_agent(user_line_extension['user_id'], agent['id'])
            queries.associate_queue_agent(queue33['id'], agent['id'])

        # Test invalid order parameter
        assert_that(
            calling(self.agentd.agents.list_user_queues).with_args(order='invalid'),
            raises(Exception),
        )

        # Test invalid direction parameter
        assert_that(
            calling(self.agentd.agents.list_user_queues).with_args(direction='invalid'),
            raises(Exception),
        )

        # Test negative limit
        assert_that(
            calling(self.agentd.agents.list_user_queues).with_args(limit=-1),
            raises(Exception),
        )

        # Test negative offset
        assert_that(
            calling(self.agentd.agents.list_user_queues).with_args(offset=-1),
            raises(Exception),
        )
