# Copyright 2013-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import datetime
import logging

from xivo_bus.resources.cti.event import AgentStatusUpdateEvent
from xivo_dao.helpers import db_utils
from wazo_amid_client.exceptions import AmidProtocolError

logger = logging.getLogger(__name__)


class LogoffAction:
    def __init__(
        self,
        amid_client,
        queue_log_manager,
        blf_manager,
        pause_manager,
        agent_status_dao,
        user_dao,
        agent_dao,
        bus_publisher,
    ):
        self._amid_client = amid_client
        self._queue_log_manager = queue_log_manager
        self._blf_manager = blf_manager
        self._pause_manager = pause_manager
        self._agent_status_dao = agent_status_dao
        self._user_dao = user_dao
        self._agent_dao = agent_dao
        self._bus_publisher = bus_publisher

    def logoff_agent(self, agent_status):
        # Precondition:
        # * agent is logged
        self._unpause_agent(agent_status)
        self._update_asterisk(agent_status)
        self._update_blf(agent_status)
        self._update_queue_log(agent_status)
        self._update_agent_status(agent_status)
        self._send_bus_status_update(agent_status)

    def _unpause_agent(self, agent_status):
        self._pause_manager.unpause_agent(agent_status)

    def _update_asterisk(self, agent_status):
        for queue in agent_status.queues:
            try:
                self._amid_client.action(
                    'QueueRemove',
                    {'Queue': queue.name, 'Interface': agent_status.interface},
                )
            except AmidProtocolError as e:
                if str(e) == 'Unable to remove interface: Not there':
                    logger.info(
                        '%s was already logged off of %s',
                        agent_status.interface,
                        queue.name,
                    )
                    continue
                raise

    def _update_blf(self, agent_status):
        agent_id = '*{}'.format(agent_status.agent_id)
        number = agent_status.agent_number
        for user_id in agent_status.user_ids:
            self._blf_manager.set_user_blf(
                user_id, 'agentstaticlogin', 'NOT_INUSE', agent_id
            )
            self._blf_manager.set_user_blf(
                user_id, 'agentstaticlogin', 'NOT_INUSE', number
            )
            self._blf_manager.set_user_blf(
                user_id, 'agentstaticlogoff', 'INUSE', agent_id
            )
            self._blf_manager.set_user_blf(
                user_id, 'agentstaticlogoff', 'INUSE', number
            )
            self._blf_manager.set_user_blf(
                user_id, 'agentstaticlogtoggle', 'NOT_INUSE', agent_id
            )
            self._blf_manager.set_user_blf(
                user_id, 'agentstaticlogtoggle', 'NOT_INUSE', number
            )

    def _update_queue_log(self, agent_status):
        login_time = self._compute_login_time(agent_status.login_at)
        self._queue_log_manager.on_agent_logged_off(
            agent_status.agent_number,
            agent_status.extension,
            agent_status.context,
            login_time,
        )

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
            tenant_uuid = self._agent_dao.agent_with_id(agent_id).tenant_uuid
            logger.debug('Found %s users.', len(users))
            headers = {
                'user_uuid:{uuid}'.format(uuid=user.uuid): True for user in users
            }
            headers['agent_id:{id}'.format(id=str(agent_id))] = True
            headers['tenant_uuid'] = tenant_uuid
            self._bus_publisher.publish(event, headers=headers)
