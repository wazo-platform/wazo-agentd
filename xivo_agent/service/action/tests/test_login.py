
# Copyright 2013-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from mock import Mock, ANY

from xivo_bus.resources.cti.event import AgentStatusUpdateEvent

from xivo_agent.queuelog import QueueLogManager
from xivo_agent.service.action.login import LoginAction
from xivo_agent.service.helper import format_agent_skills


class TestLoginAction(unittest.TestCase):

    def setUp(self):
        self.ami_client = Mock()
        self.queue_log_manager = Mock(QueueLogManager)
        self.agent_status_dao = Mock()
        self.line_dao = Mock()
        self.user_dao = Mock()
        self.bus_publisher = Mock()
        self.login_action = LoginAction(self.ami_client,
                                        self.queue_log_manager,
                                        self.agent_status_dao,
                                        self.line_dao,
                                        self.user_dao,
                                        self.bus_publisher)

    def test_login_agent(self):
        agent_id = 10
        agent_number = '10'
        queue = Mock()
        agent = Mock()
        agent.id = agent_id
        agent.number = agent_number
        agent.queues = [queue]
        extension = '1001'
        context = 'default'
        state_interface_sip = 'SIP/abcd'
        state_interface_pjsip = 'PJSIP/abcd'
        skills = format_agent_skills(agent_id)

        self.line_dao.get_interface_from_exten_and_context.return_value = state_interface_sip
        self.user_dao.find_all_by_agent_id.return_value = [Mock(uuid='42'), Mock(uuid='43')]

        self.login_action.login_agent(agent, extension, context)

        self.agent_status_dao.log_in_agent.assert_called_once_with(agent_id, agent_number, extension, context, ANY, state_interface_pjsip)
        self.agent_status_dao.add_agent_to_queues.assert_called_once_with(agent_id, agent.queues)
        self.queue_log_manager.on_agent_logged_in.assert_called_once_with(agent_number, extension, context)
        self.ami_client.queue_add.assert_called_once_with(queue.name, ANY, ANY, state_interface_pjsip, queue.penalty, skills)
        self.bus_publisher.publish.assert_called_once_with(
            AgentStatusUpdateEvent(10, AgentStatusUpdateEvent.STATUS_LOGGED_IN),
            headers={'user_uuid:42': True, 'user_uuid:43': True, 'agent_id:10': True},
        )
