# Copyright 2013-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import datetime
import unittest

from mock import ANY, call, Mock
from hamcrest import assert_that, contains_inanyorder

from wazo_agentd.service.action.logoff import LogoffAction
from wazo_amid_client.exceptions import AmidProtocolError
from xivo_bus.resources.cti.event import AgentStatusUpdateEvent


class TestLogoffAction(unittest.TestCase):
    def setUp(self):
        self.amid_client = Mock()
        self.queue_log_manager = Mock()
        self.blf_manager = Mock()
        self.agent_status_dao = Mock()
        self.user_dao = Mock()
        self.agent_dao = Mock()
        self.bus_publisher = Mock()
        self.logoff_action = LogoffAction(
            self.amid_client,
            self.queue_log_manager,
            self.blf_manager,
            self.agent_status_dao,
            self.user_dao,
            self.agent_dao,
            self.bus_publisher,
        )

    def test_logoff_agent(self):
        agent_id = 10
        user_id = 42
        agent_number = '10'
        queue_name = 'q1'
        queue = Mock()
        queue.name = queue_name
        agent_status = Mock(user_ids=[user_id])
        agent_status.agent_id = agent_id
        agent_status.agent_number = agent_number
        agent_status.login_at = datetime.datetime.utcnow()
        agent_status.queues = [queue]
        tenant_uuid = '00000000-0000-4000-8000-000000001ebc'
        self.user_dao.find_all_by_agent_id.return_value = [
            Mock(uuid='42'),
            Mock(uuid='43'),
        ]
        self.agent_dao.agent_with_id.return_value = Mock(tenant_uuid=tenant_uuid)

        self.logoff_action.logoff_agent(agent_status)

        self.amid_client.action.assert_called_once_with(
            'QueueRemove', {'Queue': queue.name, 'Interface': agent_status.interface}
        )
        assert_that(
            self.blf_manager.set_user_blf.call_args_list,
            contains_inanyorder(
                call(user_id, 'agentstaticlogin', 'NOT_INUSE', '*{}'.format(agent_id)),
                call(user_id, 'agentstaticlogin', 'NOT_INUSE', agent_number),
                call(user_id, 'agentstaticlogoff', 'INUSE', '*{}'.format(agent_id)),
                call(user_id, 'agentstaticlogoff', 'INUSE', agent_number),
                call(
                    user_id, 'agentstaticlogtoggle', 'NOT_INUSE', '*{}'.format(agent_id)
                ),
                call(user_id, 'agentstaticlogtoggle', 'NOT_INUSE', agent_number),
            ),
        )
        self.queue_log_manager.on_agent_logged_off.assert_called_once_with(
            agent_number, agent_status.extension, agent_status.context, ANY
        )
        self.agent_status_dao.remove_agent_from_all_queues.assert_called_once_with(
            agent_id
        )
        self.agent_status_dao.log_off_agent.assert_called_once_with(agent_id)
        self.bus_publisher.publish.assert_called_once_with(
            AgentStatusUpdateEvent(10, AgentStatusUpdateEvent.STATUS_LOGGED_OUT),
            headers={
                'user_uuid:42': True,
                'user_uuid:43': True,
                'agent_id:10': True,
                'tenant_uuid': tenant_uuid,
            },
        )

    def test_logoff_agent_already_off_on_asterisk(self):
        agent_id = 10
        agent_number = '10'
        queue_name = 'q1'
        queue = Mock()
        queue.name = queue_name
        agent_status = Mock(user_ids=[])
        agent_status.agent_id = agent_id
        agent_status.agent_number = agent_number
        agent_status.login_at = datetime.datetime.utcnow()
        agent_status.queues = [queue]
        self.user_dao.find_all_by_agent_id.return_value = [
            Mock(uuid='42'),
            Mock(uuid='43'),
        ]
        tenant_uuid = '00000000-0000-4000-8000-000000001ebc'
        self.agent_dao.agent_with_id.return_value = Mock(tenant_uuid=tenant_uuid)

        response = Mock()
        response.json.return_value = [
            {'Message': 'Unable to remove interface: Not there'}
        ]
        self.amid_client.action.side_effect = AmidProtocolError(response)

        self.logoff_action.logoff_agent(agent_status)

        self.amid_client.action.assert_called_once_with(
            'QueueRemove', {'Queue': queue.name, 'Interface': agent_status.interface}
        )
        self.queue_log_manager.on_agent_logged_off.assert_called_once_with(
            agent_number, agent_status.extension, agent_status.context, ANY
        )
        self.agent_status_dao.remove_agent_from_all_queues.assert_called_once_with(
            agent_id
        )
        self.agent_status_dao.log_off_agent.assert_called_once_with(agent_id)
        self.bus_publisher.publish.assert_called_once_with(
            AgentStatusUpdateEvent(10, AgentStatusUpdateEvent.STATUS_LOGGED_OUT),
            headers={
                'user_uuid:42': True,
                'user_uuid:43': True,
                'agent_id:10': True,
                'tenant_uuid': tenant_uuid,
            },
        )
