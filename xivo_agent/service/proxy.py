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

import threading


class ServiceProxy(object):

    def __init__(self):
        self._lock = threading.Lock()
        self.login_handler = None
        self.logoff_handler = None
        self.membership_handler = None
        self.on_agent_handler = None
        self.on_queue_handler = None
        self.pause_handler = None
        self.relog_handler = None
        self.status_handler = None

    def add_agent_to_queue(self, agent_id, queue_id):
        with self._lock:
            self.membership_handler.handle_add_to_queue(agent_id, queue_id)

    def remove_agent_from_queue(self, agent_id, queue_id):
        with self._lock:
            self.membership_handler.handle_remove_from_queue(agent_id, queue_id)

    def login_agent_by_id(self, agent_id, extension, context):
        with self._lock:
            self.login_handler.handle_login_by_id(agent_id, extension, context)

    def login_agent_by_number(self, agent_number, extension, context):
        with self._lock:
            self.login_handler.handle_login_by_number(agent_number, extension, context)

    def logoff_agent_by_id(self, agent_id):
        with self._lock:
            self.logoff_handler.handle_logoff_by_id(agent_id)

    def logoff_agent_by_number(self, agent_number):
        with self._lock:
            self.logoff_handler.handle_logoff_by_number(agent_number)

    def logoff_all(self):
        with self._lock:
            self.logoff_handler.handle_logoff_all()

    def relog_all(self):
        with self._lock:
            self.relog_handler.handle_relog_all()

    def pause_agent_by_number(self, agent_number, reason=None):
        with self._lock:
            self.pause_handler.handle_pause_by_number(agent_number, reason)

    def unpause_agent_by_number(self, agent_number, reason=None):
        with self._lock:
            self.pause_handler.handle_unpause_by_number(agent_number, reason)

    def get_agent_status_by_id(self, agent_id):
        with self._lock:
            return self.status_handler.handle_status_by_id(agent_id)

    def get_agent_status_by_number(self, agent_number):
        with self._lock:
            return self.status_handler.handle_status_by_number(agent_number)

    def get_agent_statuses(self):
        with self._lock:
            return self.status_handler.handle_statuses()

    def on_agent_updated(self, agent_id):
        with self._lock:
            return self.on_agent_handler.handle_on_agent_updated(agent_id)

    def on_agent_deleted(self, agent_id):
        with self._lock:
            return self.on_agent_handler.handle_on_agent_deleted(agent_id)

    def on_queue_added(self, queue_id):
        with self._lock:
            return self.on_queue_handler.handle_on_queue_added(queue_id)

    def on_queue_updated(self, queue_id):
        with self._lock:
            return self.on_queue_handler.handle_on_queue_updated(queue_id)

    def on_queue_deleted(self, queue_id):
        with self._lock:
            return self.on_queue_handler.handle_on_queue_deleted(queue_id)
