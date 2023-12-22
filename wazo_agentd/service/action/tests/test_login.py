# Copyright 2013-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import ANY, Mock, call

from hamcrest import assert_that, contains_inanyorder, has_entries
from xivo_bus.resources.agent.event import AgentStatusUpdatedEvent

from wazo_agentd.queuelog import QueueLogManager
from wazo_agentd.service.action.login import LoginAction
from wazo_agentd.service.helper import format_agent_skills
from wazo_agentd.service.manager.blf import BLFManager


class TestLoginAction(unittest.TestCase):
    def setUp(self):
        self.amid_client = Mock()
        self.queue_log_manager = Mock(QueueLogManager)
        self.blf_manager = Mock(BLFManager)
        self.agent_status_dao = Mock()
        self.line_dao = Mock()
        self.user_dao = Mock()
        self.agent_dao = Mock()
        self.bus_publisher = Mock()
        self.login_action = LoginAction(
            self.amid_client,
            self.queue_log_manager,
            self.blf_manager,
            self.agent_status_dao,
            self.line_dao,
            self.user_dao,
            self.agent_dao,
            self.bus_publisher,
        )

    def test_login_agent(self):
        user_id = 42
        agent_id = 10
        agent_number = '10'
        queue = Mock()
        agent = Mock(user_ids=[user_id])
        agent.id = agent_id
        agent.number = agent_number
        agent.queues = [queue]
        extension = '1001'
        context = 'default'
        state_interface_sip = 'PJSIP/abcd'
        skills = format_agent_skills(agent_id)
        tenant_uuid = '00000000-0000-4000-8000-000000001234'

        self.line_dao.get_interface_from_exten_and_context.return_value = (
            state_interface_sip
        )
        self.user_dao.find_all_by_agent_id.return_value = [
            Mock(uuid='42'),
            Mock(uuid='43'),
        ]
        self.amid_client.action.return_value = [{'Response': 'Ok'}]
        self.agent_dao.agent_with_id.return_value = Mock(tenant_uuid=tenant_uuid)

        self.login_action.login_agent(agent, extension, context)

        self.agent_status_dao.log_in_agent.assert_called_once_with(
            agent_id, agent_number, extension, context, ANY, state_interface_sip
        )
        self.agent_status_dao.add_agent_to_queues.assert_called_once_with(
            agent_id, agent.queues
        )
        self.queue_log_manager.on_agent_logged_in.assert_called_once_with(
            agent_number, extension, context
        )
        self.amid_client.action.assert_called_once_with(
            'QueueAdd',
            {
                'Queue': queue.name,
                'Interface': ANY,
                'MemberName': ANY,
                'StateInterface': state_interface_sip,
                'Penalty': queue.penalty,
                'Skills': skills,
            },
        )
        assert_that(
            self.blf_manager.set_user_blf.call_args_list,
            contains_inanyorder(
                call(user_id, 'agentstaticlogin', 'INUSE', f'*{agent_id}'),
                call(user_id, 'agentstaticlogin', 'INUSE', agent_number),
                call(user_id, 'agentstaticlogoff', 'NOT_INUSE', f'*{agent_id}'),
                call(user_id, 'agentstaticlogoff', 'NOT_INUSE', agent_number),
                call(user_id, 'agentstaticlogtoggle', 'INUSE', f'*{agent_id}'),
                call(user_id, 'agentstaticlogtoggle', 'INUSE', agent_number),
            ),
        )
        event = AgentStatusUpdatedEvent(10, 'logged_in', tenant_uuid, ['42', '43'])
        assert_that(
            event.headers,
            has_entries(
                {
                    'tenant_uuid': tenant_uuid,
                    'user_uuid:42': True,
                    'user_uuid:43': True,
                }
            ),
        )
        self.bus_publisher.publish.assert_called_once_with(event)

    def test_login_agent_sccp(self):
        agent_id = 10
        agent_number = '10'
        queue = Mock()
        agent = Mock(user_ids=[])
        agent.id = agent_id
        agent.number = agent_number
        agent.queues = [queue]
        extension = '1001'
        context = 'default'
        state_interface_sccp = 'SCCP/abcd'

        self.line_dao.get_interface_from_exten_and_context.return_value = (
            state_interface_sccp
        )
        self.user_dao.find_all_by_agent_id.return_value = [
            Mock(uuid='42'),
            Mock(uuid='43'),
        ]
        self.amid_client.action.return_value = [{'Response': 'Ok'}]

        self.login_action.login_agent(agent, extension, context)

        self.agent_status_dao.log_in_agent.assert_called_once_with(
            agent_id, agent_number, extension, context, ANY, state_interface_sccp
        )

    def test_login_agent_on_line(self):
        agent_id = 10
        line_id = 12
        agent_number = '10'
        queue = Mock()
        agent = Mock(user_ids=[])
        agent.id = agent_id
        agent.number = agent_number
        agent.queues = [queue]
        extension = '1001'
        context = 'default'
        state_interface_sip = 'PJSIP/abcd'
        skills = format_agent_skills(agent_id)
        tenant_uuid = '00000000-0000-4000-8000-000000001234'

        self.line_dao.get_interface_from_line_id.return_value = state_interface_sip
        self.line_dao.get_main_extension_context_from_line_id.return_value = (
            extension,
            context,
        )
        self.user_dao.find_all_by_agent_id.return_value = [
            Mock(uuid='42'),
            Mock(uuid='43'),
        ]
        self.amid_client.action.return_value = [{'Response': 'Ok'}]
        self.agent_dao.agent_with_id.return_value = Mock(tenant_uuid=tenant_uuid)

        self.login_action.login_agent_on_line(agent, line_id)

        self.agent_status_dao.log_in_agent.assert_called_once_with(
            agent_id, agent_number, extension, context, ANY, state_interface_sip
        )
        self.agent_status_dao.add_agent_to_queues.assert_called_once_with(
            agent_id, agent.queues
        )
        self.queue_log_manager.on_agent_logged_in.assert_called_once_with(
            agent_number, extension, context
        )
        self.amid_client.action.assert_called_once_with(
            'QueueAdd',
            {
                'Queue': queue.name,
                'Interface': ANY,
                'MemberName': ANY,
                'StateInterface': state_interface_sip,
                'Penalty': queue.penalty,
                'Skills': skills,
            },
        )

        event = AgentStatusUpdatedEvent(10, 'logged_in', tenant_uuid, ['42', '43'])
        assert_that(
            event.headers,
            has_entries(
                {
                    'tenant_uuid': tenant_uuid,
                    'user_uuid:42': True,
                    'user_uuid:43': True,
                }
            ),
        )
        self.bus_publisher.publish.assert_called_once_with(event)
