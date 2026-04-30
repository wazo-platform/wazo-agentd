# Copyright 2013-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from wazo_bus.resources.user_agent.event import UserAgentQueueLoggedInEvent
from xivo_dao.helpers import db_utils

logger = logging.getLogger(__name__)


class RelogManager:
    def __init__(
        self,
        login_action,
        logoff_action,
        agent_dao,
        agent_status_dao,
        user_dao,
        bus_publisher,
    ):
        self._login_action = login_action
        self._logoff_action = logoff_action
        self._agent_dao = agent_dao
        self._agent_status_dao = agent_status_dao
        self._user_dao = user_dao
        self._bus_publisher = bus_publisher

    def relog_all_agents(self, tenant_uuids=None, all_queues=False):
        agent_statuses = self._get_agent_statuses(tenant_uuids=tenant_uuids)
        for agent_status in agent_statuses:
            try:
                self._relog_agent(agent_status, all_queues=all_queues)
            except Exception:
                logger.warning(
                    'Could not relog agent %s', agent_status.agent_id, exc_info=True
                )

    def _get_agent_statuses(self, tenant_uuids=None):
        with db_utils.session_scope():
            agent_ids = self._agent_status_dao.get_logged_agent_ids(
                tenant_uuids=tenant_uuids
            )
            return [
                self._agent_status_dao.get_status(agent_id) for agent_id in agent_ids
            ]

    def _relog_agent(self, agent_status, all_queues=False):
        self._logoff_action.logoff_agent(agent_status)
        newly_logged_queues = []
        with db_utils.session_scope():
            agent = self._agent_dao.get_agent(agent_status.agent_id)
            if all_queues:
                previously_logged_ids = {
                    q.id for q in self._agent_dao.list_agent_enabled_queues(agent.id)
                }
                self._agent_status_dao.remove_agent_from_all_queues(agent.id)
                self._agent_status_dao.add_agent_to_queues(agent.id, agent.queues)
                newly_logged_queues = [
                    q for q in agent.queues if q.id not in previously_logged_ids
                ]
        self._login_action.login_agent(
            agent, agent_status.extension, agent_status.context
        )
        if newly_logged_queues:
            self._publish_queue_logged_in_events(agent, newly_logged_queues)

    def _publish_queue_logged_in_events(self, agent, queues):
        with db_utils.session_scope():
            user_uuids = [u.uuid for u in self._user_dao.find_all_by_agent_id(agent.id)]
        for queue in queues:
            event = UserAgentQueueLoggedInEvent(
                agent.id, queue.id, agent.tenant_uuid, user_uuids
            )
            self._bus_publisher.publish(event)
