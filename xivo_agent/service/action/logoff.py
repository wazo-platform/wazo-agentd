# Copyright 2013-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import datetime
import logging

from xivo_bus.resources.cti.event import AgentStatusUpdateEvent
from xivo_dao.helpers import db_utils

logger = logging.getLogger(__name__)


class LogoffAction:

    def __init__(self, ami_client, queue_log_manager, agent_status_dao, user_dao, bus_publisher):
        self._ami_client = ami_client
        self._queue_log_manager = queue_log_manager
        self._agent_status_dao = agent_status_dao
        self._user_dao = user_dao
        self._bus_publisher = bus_publisher

    def logoff_agent(self, agent_status):
        # Precondition:
        # * agent is logged
        self._update_asterisk(agent_status)
        self._update_queue_log(agent_status)
        self._update_agent_status(agent_status)
        self._update_xivo_ctid(agent_status)
        self._send_bus_status_update(agent_status)

    def _update_xivo_ctid(self, agent_status):
        self._ami_client.agent_logoff(agent_status.agent_id, agent_status.agent_number)

    def _update_asterisk(self, agent_status):
        for queue in agent_status.queues:
            self._ami_client.queue_remove(queue.name, agent_status.interface)

    def _update_queue_log(self, agent_status):
        login_time = self._compute_login_time(agent_status.login_at)
        self._queue_log_manager.on_agent_logged_off(agent_status.agent_number, agent_status.extension, agent_status.context, login_time)

    def _compute_login_time(self, login_at):
        delta = datetime.datetime.utcnow() - login_at
        return delta.total_seconds()

    def _update_agent_status(self, agent_status):
        with db_utils.session_scope():
            self._agent_status_dao.remove_agent_from_all_queues(agent_status.agent_id)
            self._agent_status_dao.log_off_agent(agent_status.agent_id)

    def _send_bus_status_update(self, agent_status):
        status = AgentStatusUpdateEvent.STATUS_LOGGED_OUT
        agent_id = agent_status.agent_id
        event = AgentStatusUpdateEvent(agent_id, status)
        with db_utils.session_scope():
            users = self._user_dao.find_all_by_agent_id(agent_id)
            logger.debug('Found %s users.', len(users))
            headers = {'user_uuid:{uuid}'.format(uuid=user.uuid): True for user in users}
            headers['agent_id:{id}'.format(id=str(agent_id))] = True
            self._bus_publisher.publish(event, headers=headers)
