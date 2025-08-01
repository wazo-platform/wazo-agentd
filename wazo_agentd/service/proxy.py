# Copyright 2015-2025 The Wazo Authors  (see the AUTHORS file)
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
        self.agent_queues_handler = None

    def add_agent_to_queue(self, agent_id, queue_id, tenant_uuids=None):
        with self._lock:
            self.membership_handler.handle_add_to_queue(
                agent_id, queue_id, tenant_uuids=tenant_uuids
            )

    def remove_agent_from_queue(self, agent_id, queue_id, tenant_uuids=None):
        with self._lock:
            self.membership_handler.handle_remove_from_queue(
                agent_id, queue_id, tenant_uuids=tenant_uuids
            )

    def list_user_queues(
        self, user_uuid, tenant_uuids=None, order=None, direction=None
    ):
        with self._lock:
            return self.agent_queues_handler.handle_list_user_queues(
                user_uuid, tenant_uuids=tenant_uuids, order=order, direction=direction
            )

    def list_queues(self, agent_id, tenant_uuids=None, order=None, direction=None):
        with self._lock:
            return self.agent_queues_handler.handle_list_queues_by_id(
                agent_id, tenant_uuids=tenant_uuids, order=order, direction=direction
            )

    def list_queues_by_number(
        self, agent_number, tenant_uuids=None, order=None, direction=None
    ):
        with self._lock:
            return self.agent_queues_handler.handle_list_queues_by_number(
                agent_number,
                tenant_uuids=tenant_uuids,
                order=order,
                direction=direction,
            )

    def login_agent_by_id(self, agent_id, extension, context, tenant_uuids=None):
        with self._lock:
            self.login_handler.handle_login_by_id(
                agent_id, extension, context, tenant_uuids=tenant_uuids
            )

    def login_agent_by_number(
        self, agent_number, extension, context, tenant_uuids=None
    ):
        with self._lock:
            self.login_handler.handle_login_by_number(
                agent_number, extension, context, tenant_uuids=tenant_uuids
            )

    def login_user_agent(self, user_uuid, line_id, tenant_uuids=None):
        with self._lock:
            self.login_handler.handle_login_user_agent(
                user_uuid, line_id, tenant_uuids=tenant_uuids
            )

    def logoff_agent_by_id(self, agent_id, tenant_uuids=None):
        with self._lock:
            self.logoff_handler.handle_logoff_by_id(agent_id, tenant_uuids=tenant_uuids)

    def logoff_agent_by_number(self, agent_number, tenant_uuids=None):
        with self._lock:
            self.logoff_handler.handle_logoff_by_number(
                agent_number, tenant_uuids=tenant_uuids
            )

    def logoff_user_agent(self, user_uuid, tenant_uuids=None):
        with self._lock:
            self.logoff_handler.handle_logoff_user_agent(
                user_uuid, tenant_uuids=tenant_uuids
            )

    def logoff_all(self, tenant_uuids=None):
        with self._lock:
            self.logoff_handler.handle_logoff_all(tenant_uuids=tenant_uuids)

    def relog_all(self, tenant_uuids=None):
        with self._lock:
            self.relog_handler.handle_relog_all(tenant_uuids=tenant_uuids)

    def pause_agent_by_number(self, agent_number, reason, tenant_uuids=None):
        with self._lock:
            self.pause_handler.handle_pause_by_number(
                agent_number, reason, tenant_uuids=tenant_uuids
            )

    def pause_user_agent(self, user_uuid, reason, tenant_uuids=None):
        with self._lock:
            self.pause_handler.handle_pause_user_agent(
                user_uuid, reason, tenant_uuids=tenant_uuids
            )

    def unpause_agent_by_number(self, agent_number, tenant_uuids=None):
        with self._lock:
            self.pause_handler.handle_unpause_by_number(
                agent_number, tenant_uuids=tenant_uuids
            )

    def unpause_user_agent(self, user_uuid, tenant_uuids=None):
        with self._lock:
            self.pause_handler.handle_unpause_user_agent(
                user_uuid, tenant_uuids=tenant_uuids
            )

    def get_agent_status_by_id(self, agent_id, tenant_uuids=None):
        with self._lock:
            return self.status_handler.handle_status_by_id(
                agent_id, tenant_uuids=tenant_uuids
            )

    def get_agent_status_by_number(self, agent_number, tenant_uuids=None):
        with self._lock:
            return self.status_handler.handle_status_by_number(
                agent_number, tenant_uuids=tenant_uuids
            )

    def get_user_agent_status(self, user_uuid, tenant_uuids=None):
        with self._lock:
            return self.status_handler.handle_status_by_user(
                user_uuid, tenant_uuids=tenant_uuids
            )

    def get_agent_statuses(self, tenant_uuids=None):
        with self._lock:
            return self.status_handler.handle_statuses(tenant_uuids=tenant_uuids)

    def on_agent_updated(self, agent):
        with self._lock:
            return self.on_agent_handler.handle_on_agent_updated(agent['id'])

    def on_agent_deleted(self, agent):
        with self._lock:
            return self.on_agent_handler.handle_on_agent_deleted(agent['id'])

    def on_queue_updated(self, queue):
        with self._lock:
            return self.on_queue_handler.handle_on_queue_updated(queue['id'])

    def on_queue_deleted(self, queue):
        with self._lock:
            return self.on_queue_handler.handle_on_queue_deleted(queue['id'])

    def on_agent_paused(self, agent):
        paused = agent['Paused'] == '1'
        with self._lock:
            if paused:
                return self.on_queue_handler.handle_on_agent_paused(agent)
            else:
                return self.on_queue_handler.handle_on_agent_unpaused(agent)
