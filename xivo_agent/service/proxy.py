# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import threading


class ServiceProxy:

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

    def login_agent_by_id(self, agent_id, extension, context, tenant_uuids=None):
        with self._lock:
            self.login_handler.handle_login_by_id(agent_id, extension, context, tenant_uuids=tenant_uuids)

    def login_agent_by_number(self, agent_number, extension, context, tenant_uuids=None):
        with self._lock:
            self.login_handler.handle_login_by_number(agent_number, extension, context, tenant_uuids=tenant_uuids)

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

    def pause_agent_by_number(self, agent_number, reason):
        with self._lock:
            self.pause_handler.handle_pause_by_number(agent_number, reason)

    def unpause_agent_by_number(self, agent_number):
        with self._lock:
            self.pause_handler.handle_unpause_by_number(agent_number)

    def get_agent_status_by_id(self, agent_id, tenant_uuids=None):
        with self._lock:
            return self.status_handler.handle_status_by_id(agent_id, tenant_uuids=tenant_uuids)

    def get_agent_status_by_number(self, agent_number, tenant_uuids=None):
        with self._lock:
            return self.status_handler.handle_status_by_number(agent_number, tenant_uuids=tenant_uuids)

    def get_agent_statuses(self, tenant_uuids=None):
        with self._lock:
            return self.status_handler.handle_statuses(tenant_uuids=tenant_uuids)

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

    def on_agent_paused(self, *args, **kwargs):
        with self._lock:
            return self.on_queue_handler.handle_on_agent_paused(*args, **kwargs)

    def on_agent_unpaused(self, *args, **kwargs):
        with self._lock:
            return self.on_queue_handler.handle_on_agent_unpaused(*args, **kwargs)
