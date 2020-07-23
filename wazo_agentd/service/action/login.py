# Copyright 2013-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from wazo_agentd.exception import NoSuchExtensionError
from wazo_agentd.service.helper import format_agent_member_name, format_agent_skills
from xivo_bus.resources.cti.event import AgentStatusUpdateEvent
from xivo_dao.helpers import db_utils

logger = logging.getLogger(__name__)


class LoginAction:
    def __init__(
        self,
        amid_client,
        queue_log_manager,
        agent_status_dao,
        line_dao,
        user_dao,
        bus_publisher,
    ):
        self._amid_client = amid_client
        self._queue_log_manager = queue_log_manager
        self._agent_status_dao = agent_status_dao
        self._line_dao = line_dao
        self._user_dao = user_dao
        self._bus_publisher = bus_publisher

    def login_agent(self, agent, extension, context):
        # Precondition:
        # * agent is not logged
        # * extension@context is not used
        interface = self._get_interface(agent)
        state_interface = self._get_state_interface(extension, context)

        # TODO PJSIP: clean after migration
        if state_interface.startswith('SIP/'):
            state_interface = 'PJ{}'.format(state_interface)
        if state_interface.startswith('sip/'):
            state_interface = 'pj{}'.format(state_interface)

        self._update_agent_status(agent, extension, context, interface, state_interface)
        self._update_queue_log(agent, extension, context)
        self._update_asterisk(agent, interface, state_interface)
        self._send_bus_status_update(agent)

    def _get_interface(self, agent):
        return 'Local/id-{0}@agentcallback'.format(agent.id)

    def _get_state_interface(self, extension, context):
        try:
            with db_utils.session_scope():
                return self._line_dao.get_interface_from_exten_and_context(
                    extension, context
                )
        except LookupError:
            raise NoSuchExtensionError(extension, context)

    def _update_agent_status(
        self, agent, extension, context, interface, state_interface
    ):
        with db_utils.session_scope():
            self._agent_status_dao.log_in_agent(
                agent.id, agent.number, extension, context, interface, state_interface
            )
            self._agent_status_dao.add_agent_to_queues(agent.id, agent.queues)

    def _update_queue_log(self, agent, extension, context):
        self._queue_log_manager.on_agent_logged_in(agent.number, extension, context)

    def _update_asterisk(self, agent, interface, state_interface):
        member_name = format_agent_member_name(agent.number)
        skills = format_agent_skills(agent.id)
        for queue in agent.queues:
            response = self._amid_client.action(
                'QueueAdd',
                {
                    'Queue': queue.name,
                    'Interface': interface,
                    'MemberName': member_name,
                    'StateInterface': state_interface,
                    'Penalty': queue.penalty,
                    'Skills': skills,
                },
            )
            if response[0]['Response'] != 'Success':
                logger.warning(
                    'Failure to add interface %r to queue %r', interface, queue.name
                )

    def _send_bus_status_update(self, agent):
        status = AgentStatusUpdateEvent.STATUS_LOGGED_IN
        event = AgentStatusUpdateEvent(agent.id, status)
        logger.debug('Looking for users with agent id %s...', agent.id)
        with db_utils.session_scope():
            users = self._user_dao.find_all_by_agent_id(agent.id)
            logger.debug('Found %s users.', len(users))
            headers = {
                'user_uuid:{uuid}'.format(uuid=user.uuid): True for user in users
            }
            headers['agent_id:{id}'.format(id=str(agent.id))] = True
            self._bus_publisher.publish(event, headers=headers)
