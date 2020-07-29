# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, calling, has_properties, is_

from wazo_agentd_client.error import (
    AgentdClientError,
    NO_SUCH_AGENT,
    NO_SUCH_LINE,
    UNAUTHORIZED,
)
from xivo_test_helpers.hamcrest.raises import raises

from .helpers.base import BaseIntegrationTest, UNKNOWN_UUID, UNKNOWN_ID
from .helpers import associations, fixtures


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
                has_properties(error='invalid fields: extension, context'),
            ),
        )

    @fixtures.user_line_extension(exten='1001', context='default')
    @fixtures.agent()
    def test_login_logoff(self, user_line_extension, agent):

        self.agentd.agents.login_agent(
            agent['id'], user_line_extension['exten'], user_line_extension['context'],
        )

        status = self.agentd.agents.get_agent_status(agent['id'])
        assert_that(status.logged, is_(True))

        self.agentd.agents.logoff_agent(agent['id'])

        status = self.agentd.agents.get_agent_status(agent['id'])
        assert_that(status.logged, is_(False))

    @fixtures.user_line_extension(exten='1001', context='default', name_line='abcdef')
    @fixtures.agent(number='1234')
    def test_agent_status(self, user_line_extension, agent):

        self.agentd.agents.login_agent(
            agent['id'], user_line_extension['exten'], user_line_extension['context'],
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
                    'paused': False,
                    'paused_reason': None,
                    'state_interface': 'PJSIP/abcdef',
                }
            ),
        )

    @fixtures.user_line_extension(exten='1001', context='default', name_line='abcdef')
    @fixtures.agent(number='1234')
    def test_login_logoff_user_agent_on_specific_line(self, user_line_extension, agent):
        self.create_user_token(user_line_extension['user_uuid'])

        with associations.user_agent(
            self.database, user_line_extension['user_id'], agent['id']
        ):
            # login
            self.agentd.agents.login_user_agent(user_line_extension['line_id'])

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
                    }
                ),
            )

            # logoff
            self.agentd.agents.logoff_user_agent()

            status = self.agentd.agents.get_agent_status(agent['id'])
            assert_that(
                status,
                has_properties(
                    {
                        'id': agent['id'],
                        'logged': False,
                        'context': None,
                        'extension': None,
                        'number': '1234',
                        'state_interface': None,
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
    def test_login_logoff_user_agent_without_agent(self, user_line_extension):
        self.create_user_token(user_line_extension['user_uuid'])

        # login
        assert_that(
            calling(self.agentd.agents.login_user_agent).with_args(
                user_line_extension['line_id']
            ),
            raises(AgentdClientError, has_properties(error=NO_SUCH_AGENT)),
        )
        # logoff
        assert_that(
            calling(self.agentd.agents.logoff_user_agent),
            raises(AgentdClientError, has_properties(error=NO_SUCH_AGENT)),
        )

    @fixtures.user_line_extension(exten='1001', context='default', name_line='abcdef')
    def test_login_logoff_user_agent_without_user(self, user_line_extension):
        self.create_user_token(UNKNOWN_UUID)

        # login
        assert_that(
            calling(self.agentd.agents.login_user_agent).with_args(
                user_line_extension['line_id']
            ),
            raises(AgentdClientError, has_properties(error=NO_SUCH_AGENT)),
        )

        # logoff
        assert_that(
            calling(self.agentd.agents.logoff_user_agent),
            raises(AgentdClientError, has_properties(error=NO_SUCH_AGENT)),
        )
