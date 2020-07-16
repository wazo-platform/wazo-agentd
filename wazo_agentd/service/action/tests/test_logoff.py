# Copyright 2013-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import datetime
import unittest

from mock import Mock, ANY

from xivo_bus.resources.cti.event import AgentStatusUpdateEvent

from wazo_agentd.service.action.logoff import LogoffAction


class TestLogoffAction(unittest.TestCase):
    def setUp(self):
        self.amid_client = Mock()
        self.queue_log_manager = Mock()
        self.agent_status_dao = Mock()
        self.user_dao = Mock()
        self.bus_publisher = Mock()
        self.logoff_action = LogoffAction(
            self.amid_client,
            self.queue_log_manager,
            self.agent_status_dao,
            self.user_dao,
            self.bus_publisher,
        )

    def test_logoff_agent(self):
        agent_id = 10
        agent_number = '10'
        queue_name = 'q1'
        queue = Mock()
        queue.name = queue_name
        agent_status = Mock()
        agent_status.agent_id = agent_id
        agent_status.agent_number = agent_number
        agent_status.login_at = datetime.datetime.utcnow()
        agent_status.queues = [queue]
        self.user_dao.find_all_by_agent_id.return_value = [
            Mock(uuid='42'),
            Mock(uuid='43'),
        ]

        self.logoff_action.logoff_agent(agent_status)

        self.amid_client.action.assert_called_once_with(
            'QueueRemove',
            {
                'Queue': queue.name,
                'Interface': agent_status.interface,
            }
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
            headers={'user_uuid:42': True, 'user_uuid:43': True, 'agent_id:10': True},
        )
