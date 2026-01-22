# Copyright 2019-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import json

from hamcrest import (
    all_of,
    assert_that,
    calling,
    has_entries,
    has_items,
    has_properties,
    is_,
    matches_regexp,
)
from wazo_agentd_client.error import (
    NO_SUCH_AGENT,
    NO_SUCH_EXTEN,
    NO_SUCH_LINE,
    NOT_LOGGED,
    UNAUTHORIZED,
    AgentdClientError,
)
from wazo_test_helpers import until
from wazo_test_helpers.hamcrest.raises import raises

from .helpers import associations, fixtures
from .helpers.base import UNKNOWN_ID, UNKNOWN_UUID, BaseIntegrationTest


class TestAgents(BaseIntegrationTest):
    asset = 'base'

    def test_authentication(self):
        agentd_client = self.make_agentd(token=UNKNOWN_UUID)
        assert_that(
            calling(agentd_client.agents.get_agent_statuses),
            raises(AgentdClientError, has_properties(error=UNAUTHORIZED)),
        )

    def test_login_wrong_parameters(self):
        SOME_INTEGER = 1234

        assert_that(
            calling(self.agentd.agents.login_agent).with_args(
                UNKNOWN_ID, SOME_INTEGER, SOME_INTEGER
            ),
            raises(
                AgentdClientError,
                has_properties(
                    error=all_of(
                        matches_regexp('invalid fields: .*'),
                        matches_regexp('extension'),
                        matches_regexp('context'),
                    )
                ),
            ),
        )

    @fixtures.user_line_extension(exten='1001', context='default')
    @fixtures.agent()
    def test_login_logoff(self, user_line_extension, agent):
        self.agentd.agents.login_agent(
            agent['id'],
            user_line_extension['exten'],
            user_line_extension['context'],
        )

        status = self.agentd.agents.get_agent_status(agent['id'])
        assert_that(status.logged, is_(True))

        self.agentd.agents.logoff_agent(agent['id'])

        status = self.agentd.agents.get_agent_status(agent['id'])
        assert_that(status.logged, is_(False))

    @fixtures.user_line_extension(exten='1001', context='default', name_line='abcdef')
    @fixtures.user_line_extension(exten='1002', context='default', name_line='ghijkl')
    @fixtures.agent(number='1001')
    def test_login_on_specific_endpoint(
        self, user_line_extension, another_user_line_extension, agent
    ):
        self.agentd.agents.login_agent(
            agent['id'],
            user_line_extension['exten'],
            user_line_extension['context'],
            endpoint='PJSIP/abcdef',
        )

        status = self.agentd.agents.get_agent_status(agent['id'])
        assert_that(
            status,
            has_properties(
                {
                    'id': agent['id'],
                    'logged': True,
                    'context': 'default',
                    'extension': '1001',
                    'number': '1001',
                    'state_interface': 'PJSIP/abcdef',
                    'queues': [],
                }
            ),
        )

        self.agentd.agents.logoff_agent(agent['id'])

        status = self.agentd.agents.get_agent_status(agent['id'])
        assert_that(status.logged, is_(False))

        assert_that(
            calling(self.agentd.agents.login_agent).with_args(
                agent['id'],
                user_line_extension['exten'],
                user_line_extension['context'],
                endpoint='PJSIP/ghijkl',
            ),
            raises(AgentdClientError, has_properties(error=NO_SUCH_EXTEN)),
        )

    @fixtures.user_line_extension(exten='1001', context='default', name_line='abcdef')
    @fixtures.agent(number='1234')
    def test_agent_status(self, user_line_extension, agent):
        self.agentd.agents.login_agent(
            agent['id'],
            user_line_extension['exten'],
            user_line_extension['context'],
        )

        status = self.agentd.agents.get_agent_status(agent['id'])
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
                    'queues': [],
                }
            ),
        )

    @fixtures.user_line_extension(exten='1001', context='default', name_line='abcdef')
    @fixtures.agent(number='1234')
    def test_login_pause_unpause_logoff_user_agent_on_specific_line(
        self, user_line_extension, agent
    ):
        self.create_user_token(user_line_extension['user_uuid'])

        with associations.user_agent(
            self.database, user_line_extension['user_id'], agent['id']
        ):
            # login
            self.agentd.agents.login_user_agent(user_line_extension['line_id'])

            status = self.agentd.agents.get_user_agent_status()
            assert_that(
                status,
                has_properties(
                    {
                        'id': agent['id'],
                        'logged': True,
                        'paused': False,
                        'context': 'default',
                        'extension': '1001',
                        'number': '1234',
                        'state_interface': 'PJSIP/abcdef',
                        'queues': [],
                    }
                ),
            )

            # pause
            self.agentd.agents.pause_user_agent()
            self.bus.send_queue_member_pause('1234', agent['id'], paused=True)

            def test_on_msg_received():
                status = self.agentd.agents.get_user_agent_status()
                assert_that(status, has_properties(paused=True))

            until.assert_(test_on_msg_received, tries=10)

            # unpause
            self.agentd.agents.unpause_user_agent()
            self.bus.send_queue_member_pause('1234', agent['id'], paused=False)

            def test_on_msg_received():
                status = self.agentd.agents.get_user_agent_status()
                assert_that(status, has_properties(paused=False))

            until.assert_(test_on_msg_received, tries=10)

            # logoff
            self.agentd.agents.logoff_user_agent()

            status = self.agentd.agents.get_user_agent_status()
            assert_that(
                status,
                has_properties(
                    {
                        'id': agent['id'],
                        'logged': False,
                        'paused': False,
                        'context': None,
                        'extension': None,
                        'number': '1234',
                        'state_interface': None,
                        'queues': [],
                    }
                ),
            )

    @fixtures.user_line_extension(exten='1001', context='default', name_line='abcdef')
    @fixtures.agent(number='1234')
    def test_login_user_agent_on_unknown_line(self, user_line_extension, agent):
        self.create_user_token(user_line_extension['user_uuid'])

        with associations.user_agent(
            self.database, user_line_extension['user_id'], agent['id']
        ):
            assert_that(
                calling(self.agentd.agents.login_user_agent).with_args(UNKNOWN_ID),
                raises(AgentdClientError, has_properties(error=NO_SUCH_LINE)),
            )

    @fixtures.user_line_extension(exten='1001', context='default', name_line='abcdef')
    @fixtures.user_line_extension(exten='1002', context='default', name_line='ghijkl')
    @fixtures.agent(number='1234')
    def test_login_user_agent_on_someone_else_line(
        self, user_line_extension, other_user_line_extension, agent
    ):
        self.create_user_token(user_line_extension['user_uuid'])

        with associations.user_agent(
            self.database, user_line_extension['user_id'], agent['id']
        ):
            assert_that(
                calling(self.agentd.agents.login_user_agent).with_args(
                    other_user_line_extension['line_id']
                ),
                raises(AgentdClientError, has_properties(error=NO_SUCH_LINE)),
            )

    @fixtures.user_line_extension(exten='1001', context='default', name_line='abcdef')
    def test_get_login_pause_unpause_logoff_user_agent_without_agent(
        self, user_line_extension
    ):
        self.create_user_token(user_line_extension['user_uuid'])

        # get
        assert_that(
            calling(self.agentd.agents.get_user_agent_status),
            raises(AgentdClientError, has_properties(error=NO_SUCH_AGENT)),
        )

        # login
        assert_that(
            calling(self.agentd.agents.login_user_agent).with_args(
                user_line_extension['line_id']
            ),
            raises(AgentdClientError, has_properties(error=NO_SUCH_AGENT)),
        )

        # pause
        assert_that(
            calling(self.agentd.agents.pause_user_agent),
            raises(AgentdClientError, has_properties(error=NO_SUCH_AGENT)),
        )

        # unpause
        assert_that(
            calling(self.agentd.agents.unpause_user_agent),
            raises(AgentdClientError, has_properties(error=NO_SUCH_AGENT)),
        )

        # logoff
        assert_that(
            calling(self.agentd.agents.logoff_user_agent),
            raises(AgentdClientError, has_properties(error=NO_SUCH_AGENT)),
        )

    @fixtures.user_line_extension(exten='1001', context='default', name_line='abcdef')
    def test_login_pause_unpause_logoff_user_agent_without_user(
        self, user_line_extension
    ):
        self.create_user_token(UNKNOWN_UUID)

        # get
        assert_that(
            calling(self.agentd.agents.get_user_agent_status),
            raises(AgentdClientError, has_properties(error=NO_SUCH_AGENT)),
        )

        # login
        assert_that(
            calling(self.agentd.agents.login_user_agent).with_args(
                user_line_extension['line_id']
            ),
            raises(AgentdClientError, has_properties(error=NO_SUCH_AGENT)),
        )

        # pause
        assert_that(
            calling(self.agentd.agents.pause_user_agent),
            raises(AgentdClientError, has_properties(error=NO_SUCH_AGENT)),
        )

        # unpause
        assert_that(
            calling(self.agentd.agents.unpause_user_agent),
            raises(AgentdClientError, has_properties(error=NO_SUCH_AGENT)),
        )

        # logoff
        assert_that(
            calling(self.agentd.agents.logoff_user_agent),
            raises(AgentdClientError, has_properties(error=NO_SUCH_AGENT)),
        )

    @fixtures.agent(id=42, number='1234')
    @fixtures.user_line_extension(
        agentid=42, exten='1001', context='default', name_line='ab'
    )
    def test_pause_unpause_logoff_user_agent_not_logged(
        self, agent, user_line_extension
    ):
        self.create_user_token(user_line_extension['user_uuid'])

        # pause
        assert_that(
            calling(self.agentd.agents.pause_agent_by_number).with_args('1234'),
            raises(AgentdClientError, has_properties(error=NOT_LOGGED)),
        )
        assert_that(
            calling(self.agentd.agents.pause_user_agent),
            raises(AgentdClientError, has_properties(error=NOT_LOGGED)),
        )

        # unpause
        assert_that(
            calling(self.agentd.agents.unpause_agent_by_number).with_args('1234'),
            raises(AgentdClientError, has_properties(error=NOT_LOGGED)),
        )
        assert_that(
            calling(self.agentd.agents.unpause_user_agent),
            raises(AgentdClientError, has_properties(error=NOT_LOGGED)),
        )

        # logoff
        assert_that(
            calling(self.agentd.agents.logoff_agent_by_number).with_args('1234'),
            raises(AgentdClientError, has_properties(error=NOT_LOGGED)),
        )
        assert_that(
            calling(self.agentd.agents.logoff_user_agent),
            raises(AgentdClientError, has_properties(error=NOT_LOGGED)),
        )

    @fixtures.user_line_extension(exten='1001', context='default')
    @fixtures.agent()
    @fixtures.queue()
    def test_user_agent_login_to_queue(self, user_line_extension, agent, queue):
        self.agentd.agents.login_agent(
            agent['id'],
            user_line_extension['exten'],
            user_line_extension['context'],
        )

        self.create_user_token(user_line_extension['user_uuid'])

        with associations.user_agent(
            self.database, user_line_extension['user_id'], agent['id']
        ):
            with self.database.queries() as db:
                db.associate_queue_agent(queue['id'], agent['id'])

            status = self.agentd.agents.get_agent_status(agent['id'])
            assert status.logged is True
            assert status.queues[0]['logged'] is False

            accumulator = self.bus.accumulator(
                headers={'name': 'user_agent_queue_logged_in'}
            )
            self.agentd.agents.user_agent_login_to_queue(queue['id'])

            accumulator.until_assert_that_accumulate(
                has_items(
                    has_entries(
                        {f'user_uuid:{user_line_extension["user_uuid"]}': True},
                        data=has_entries(
                            agent_id=agent['id'],
                            queue_id=queue['id'],
                        ),
                    ),
                )
            )

            status = self.agentd.agents.get_agent_status(agent['id'])
            assert status.logged is True
            assert status.queues[0]['logged'] is True

    @fixtures.user_line_extension(exten='1001', context='default')
    @fixtures.agent()
    @fixtures.queue()
    def test_user_agent_logoff_from_queue(self, user_line_extension, agent, queue):
        self.agentd.agents.login_agent(
            agent['id'],
            user_line_extension['exten'],
            user_line_extension['context'],
        )

        self.agentd.agents.add_agent_to_queue(agent['id'], queue['id'])
        self.create_user_token(user_line_extension['user_uuid'])

        with associations.user_agent(
            self.database, user_line_extension['user_id'], agent['id']
        ):
            status = self.agentd.agents.get_agent_status(agent['id'])
            assert status.logged is True
            assert status.queues[0]['logged'] is True

            accumulator = self.bus.accumulator(
                headers={'name': 'user_agent_queue_logged_off'}
            )
            self.agentd.agents.user_agent_logoff_from_queue(queue['id'])

            accumulator.until_assert_that_accumulate(
                has_items(
                    has_entries(
                        {f'user_uuid:{user_line_extension["user_uuid"]}': True},
                        data=has_entries(
                            agent_id=agent['id'],
                            queue_id=queue['id'],
                        ),
                    ),
                )
            )

            status = self.agentd.agents.get_agent_status(agent['id'])
            assert status.logged is True
            assert status.queues[0]['logged'] is False

    @fixtures.user_line_extension(exten='1001', context='default')
    @fixtures.agent()
    @fixtures.queue()
    @fixtures.queue()
    def test_agent_login_logoff_preserves_queue_status(
        self, user_line_extension, agent, queue_1, queue_2
    ):
        self.create_user_token(user_line_extension['user_uuid'])

        with associations.user_agent(
            self.database, user_line_extension['user_id'], agent['id']
        ):
            with self.database.queries() as db:
                db.associate_queue_agent(queue_1['id'], agent['id'])
                db.associate_queue_agent(queue_2['id'], agent['id'])
                db.insert_agent_membership_status(queue_1['id'], agent['id'])

            self.agentd.agents.login_agent(
                agent['id'],
                user_line_extension['exten'],
                user_line_extension['context'],
            )

            status = self.agentd.agents.get_agent_status(agent['id'])
            assert status.logged is True
            assert status.queues[0]['logged'] is True
            assert status.queues[1]['logged'] is False

            self.agentd.agents.user_agent_logoff_from_queue(queue_1['id'])
            self.agentd.agents.user_agent_login_to_queue(queue_2['id'])
            self.agentd.agents.logoff_agent(agent['id'])

            status = self.agentd.agents.get_agent_status(agent['id'])
            assert status.logged is False

            self.agentd.agents.login_agent(
                agent['id'],
                user_line_extension['exten'],
                user_line_extension['context'],
            )

            status = self.agentd.agents.get_agent_status(agent['id'])
            assert status.logged is True
            assert status.queues[0]['logged'] is False
            assert status.queues[1]['logged'] is True

    @fixtures.user_line_extension(exten='1001', context='default')
    @fixtures.agent(number='1234')
    @fixtures.queue(name='Queue1')
    def test_adding_queue_to_logged_off_agent_enables_it_for_next_login(
        self, user_line_extension, agent, queue
    ):
        with associations.user_agent(
            self.database, user_line_extension['user_id'], agent['id']
        ):
            self.agentd.agents.add_agent_to_queue(agent['id'], queue['id'])

            status = self.agentd.agents.get_agent_status(agent['id'])
            assert status.logged is False

            self.amid.reset()

            self.agentd.agents.login_agent(
                agent['id'],
                user_line_extension['exten'],
                user_line_extension['context'],
            )

            status = self.agentd.agents.get_agent_status(agent['id'])
            assert status.logged is True
            assert status.queues[0]['logged'] is True

            for request in self.amid.get_requests()['requests']:
                body = json.loads(request['body'])
                if (
                    request['path'].endswith('action/QueueAdd')
                    and body.get('Queue') == queue['name']
                    and body.get('MemberName') == f'Agent/{agent["number"]}'
                ):
                    break
            else:
                raise AssertionError('No such AMI QueueAdd event')
