# Copyright 2019-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import json
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

    @fixtures.user_line_extension(exten='1001', context='default')
    @fixtures.agent(number='1234')
    @fixtures.queue()
    def test_on_queue_member_agent_associated(self, user_line_extension, agent, queue):
        with self.database.queries() as queries:
            with queries.inserter() as inserter:
                inserter.add_agent_login_status(
                    agent_id=agent['id'], agent_number=agent['number']
                )
            queries.associate_user_agent(user_line_extension['user_id'], agent['id'])
            queries.associate_queue_agent(queue['id'], agent['id'])

        self.amid.reset()
        self.bus.send_queue_member_agent_associated(agent['id'], queue['id'], 1)

        def assert_ami_command_received():
            requests = self.amid.get_requests().get('requests', [])
            for request in requests:
                if body := json.loads(request['body']):
                    if (
                        body['MemberName'] == f'Agent/{agent["number"]}'
                        and body['Paused'] == '0'
                        and 'Reason' not in body
                        and body['Penalty'] == 1
                        and request['path'].endswith('QueueAdd')
                    ):
                        return
            raise AssertionError('AMI QueueAdd action not received')

        until.assert_(assert_ami_command_received, tries=10)

        status = self.agentd.agents.get_agent_status(agent['id'])
        assert status.logged is True
        assert status.queues[0]['logged'] is True

    @fixtures.user_line_extension(exten='1001', context='default')
    @fixtures.agent(number='1234')
    @fixtures.queue()
    def test_on_queue_member_agent_associated_while_paused(
        self, user_line_extension, agent, queue
    ):
        with self.database.queries() as queries:
            with queries.inserter() as inserter:
                inserter.add_agent_login_status(
                    agent_id=agent['id'],
                    agent_number=agent['number'],
                    paused=True,
                    paused_reason='for some reason',
                )
            queries.associate_user_agent(user_line_extension['user_id'], agent['id'])
            queries.associate_queue_agent(queue['id'], agent['id'])

        self.amid.reset()
        self.bus.send_queue_member_agent_associated(agent['id'], queue['id'], 16)

        def assert_ami_command_received():
            requests = self.amid.get_requests().get('requests', [])
            for request in requests:
                if body := json.loads(request['body']):
                    if (
                        body['MemberName'] == f'Agent/{agent["number"]}'
                        and body['Paused'] == '1'
                        and body['Reason'] == 'for some reason'
                        and body['Penalty'] == 16
                        and request['path'].endswith('QueueAdd')
                    ):
                        return
            raise AssertionError('AMI QueueAdd action not received')

        until.assert_(assert_ami_command_received, tries=10)

        status = self.agentd.agents.get_agent_status(agent['id'])
        assert status.logged is True
        assert status.queues[0]['logged'] is True
        assert status.queues[0]['paused'] is True
        assert status.queues[0]['paused_reason'] == 'for some reason'

    @fixtures.user_line_extension(exten='1001', context='default')
    @fixtures.agent(number='1234')
    @fixtures.queue()
    def test_on_queue_member_agent_associated_while_logged_off(
        self, user_line_extension, agent, queue
    ):
        with self.database.queries() as queries:
            queries.associate_user_agent(user_line_extension['user_id'], agent['id'])
            queries.associate_queue_agent(queue['id'], agent['id'])

        self.amid.reset()
        self.bus.send_queue_member_agent_associated(agent['id'], queue['id'], 64)

        def assert_queue_is_enabled(queries):
            membership = queries.get_agent_membership_status(queue['id'], agent['id'])
            assert membership is not None

        with self.database.queries() as queries:
            until.assert_(assert_queue_is_enabled, queries, tries=10)

        assert len(self.amid.get_requests()['requests']) == 0

        status = self.agentd.agents.get_agent_status(agent['id'])
        assert status.logged is False
        assert len(status.queues) == 0

        self.agentd.agents.login_agent(
            agent['id'], user_line_extension['exten'], user_line_extension['context']
        )

        status = self.agentd.agents.get_agent_status(agent['id'])
        assert status.logged is True
        assert status.queues[0]['logged'] is True

    @fixtures.user_line_extension(exten='1001', context='default')
    @fixtures.agent(number='1234')
    @fixtures.queue()
    def test_on_queue_member_agent_dissociated(self, user_line_extension, agent, queue):
        with self.database.queries() as queries:
            queries.associate_user_agent(user_line_extension['user_id'], agent['id'])
            queries.associate_queue_agent(queue['id'], agent['id'])
            queries.insert_agent_membership_status(queue['id'], agent['id'])
            with queries.inserter() as inserter:
                inserter.add_agent_login_status(
                    agent_id=agent['id'], agent_number=agent['number']
                )

        self.amid.reset()
        self.bus.send_queue_member_agent_dissociated(agent['id'], queue['id'])

        def assert_ami_command_received():
            requests = self.amid.get_requests().get('requests', [])
            for request in requests:
                if request['path'].endswith('QueueRemove'):
                    return
            raise AssertionError('AMI QueueRemove action not received')

        until.assert_(assert_ami_command_received, tries=10)

        with self.database.queries() as queries:
            membership = queries.get_agent_membership_status(queue['id'], agent['id'])
            assert membership is None
