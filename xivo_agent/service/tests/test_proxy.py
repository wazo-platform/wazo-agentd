# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import unittest

from mock import Mock, sentinel as s
from xivo_agent.service.handler.login import LoginHandler
from xivo_agent.service.handler.logoff import LogoffHandler
from xivo_agent.service.handler.membership import MembershipHandler
from xivo_agent.service.handler.on_agent import OnAgentHandler
from xivo_agent.service.handler.on_queue import OnQueueHandler
from xivo_agent.service.handler.pause import PauseHandler
from xivo_agent.service.handler.relog import RelogHandler
from xivo_agent.service.handler.status import StatusHandler
from xivo_agent.service.proxy import ServiceProxy


class TestServiceProxy(unittest.TestCase):

    def setUp(self):
        self.login_handler = Mock(LoginHandler)
        self.logoff_handler = Mock(LogoffHandler)
        self.membership_handler = Mock(MembershipHandler)
        self.on_agent_handler = Mock(OnAgentHandler)
        self.on_queue_handler = Mock(OnQueueHandler)
        self.pause_handler = Mock(PauseHandler)
        self.relog_handler = Mock(RelogHandler)
        self.status_handler = Mock(StatusHandler)
        self.proxy = ServiceProxy()
        self.proxy.login_handler = self.login_handler
        self.proxy.logoff_handler = self.logoff_handler
        self.proxy.membership_handler = self.membership_handler
        self.proxy.on_agent_handler = self.on_agent_handler
        self.proxy.on_queue_handler = self.on_queue_handler
        self.proxy.pause_handler = self.pause_handler
        self.proxy.relog_handler = self.relog_handler
        self.proxy.status_handler = self.status_handler

    def test_add_agent_to_queue(self):
        self.proxy.add_agent_to_queue(s.agent_id, s.queue_id)

        self.membership_handler.handle_add_to_queue.assert_called_once_with(s.agent_id, s.queue_id)

    def test_remove_agent_from_queue(self):
        self.proxy.remove_agent_from_queue(s.agent_id, s.queue_id)

        self.membership_handler.handle_remove_from_queue.assert_called_once_with(s.agent_id, s.queue_id)

    def test_login_agent_by_id(self):
        self.proxy.login_agent_by_id(s.agent_id, s.extension, s.context)

        self.login_handler.handle_login_by_id.assert_called_once_with(s.agent_id, s.extension, s.context)

    def test_login_agent_by_number(self):
        self.proxy.login_agent_by_number(s.agent_number, s.extension, s.context)

        self.login_handler.handle_login_by_number.assert_called_once_with(s.agent_number, s.extension, s.context)

    def test_logoff_agent_by_id(self):
        self.proxy.logoff_agent_by_id(s.agent_id)

        self.logoff_handler.handle_logoff_by_id.assert_called_once_with(s.agent_id)

    def test_logoff_agent_by_number(self):
        self.proxy.logoff_agent_by_number(s.agent_number)

        self.logoff_handler.handle_logoff_by_number.assert_called_once_with(s.agent_number)

    def test_logoff_all(self):
        self.proxy.logoff_all()

        self.logoff_handler.handle_logoff_all.assert_called_once_with()

    def test_relog_all(self):
        self.proxy.relog_all()

        self.relog_handler.handle_relog_all.assert_called_once_with()

    def test_pause_agent_by_number(self):
        self.proxy.pause_agent_by_number(s.agent_number)

        self.pause_handler.handle_pause_by_number.assert_called_once_with(s.agent_number)

    def test_unpause_agent_by_number(self):
        self.proxy.unpause_agent_by_number(s.agent_number)

        self.pause_handler.handle_unpause_by_number.assert_called_once_with(s.agent_number)

    def test_get_agent_status_by_id(self):
        self.proxy.get_agent_status_by_id(s.agent_id)

        self.status_handler.handle_status_by_id.assert_called_once_with(s.agent_id)

    def test_get_agent_status_by_number(self):
        self.proxy.get_agent_status_by_number(s.agent_number)

        self.status_handler.handle_status_by_number.assert_called_once_with(s.agent_number)

    def test_get_agent_statuses(self):
        self.proxy.get_agent_statuses()

        self.status_handler.handle_statuses.assert_called_once_with()

    def test_on_agent_updated(self):
        self.proxy.on_agent_updated(s.agent_id)

        self.on_agent_handler.handle_on_agent_updated.assert_called_once_with(s.agent_id)

    def test_on_agent_deleted(self):
        self.proxy.on_agent_deleted(s.agent_id)

        self.on_agent_handler.handle_on_agent_deleted.assert_called_once_with(s.agent_id)

    def test_on_queue_added(self):
        self.proxy.on_queue_added(s.queue_id)

        self.on_queue_handler.handle_on_queue_added.assert_called_once_with(s.queue_id)

    def test_on_queue_updated(self):
        self.proxy.on_queue_updated(s.queue_id)

        self.on_queue_handler.handle_on_queue_updated.assert_called_once_with(s.queue_id)

    def test_on_queue_deleted(self):
        self.proxy.on_queue_deleted(s.queue_id)

        self.on_queue_handler.handle_on_queue_deleted.assert_called_once_with(s.queue_id)
