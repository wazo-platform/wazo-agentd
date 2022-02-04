# Copyright 2013-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from wazo_agentd.exception import NoSuchExtensionError, NoSuchLineError
from wazo_agentd.service.helper import format_agent_member_name, format_agent_skills
from xivo_bus.resources.cti.event import AgentStatusUpdateEvent
from xivo_dao.helpers import db_utils

logger = logging.getLogger(__name__)


class LoginAction:
    def __init__(
        self,
        amid_client,
        queue_log_manager,
        blf_manager,
        agent_status_dao,
        line_dao,
        user_dao,
        agent_dao,
        bus_publisher,
    ):
        self._amid_client = amid_client
        self._blf_manager = blf_manager
        self._queue_log_manager = queue_log_manager
        self._agent_status_dao = agent_status_dao
        self._line_dao = line_dao
        self._user_dao = user_dao
        self._agent_dao = agent_dao
        self._bus_publisher = bus_publisher

    def login_agent(self, agent, extension, context):
        # Precondition:
        # * agent is not logged
        # * extension@context is not used
        interface = self._get_interface(agent)
        state_interface = self._get_state_interface(extension, context)

        self._do_login(agent, extension, context, interface, state_interface)

    def login_agent_on_line(self, agent, line_id):
        # Precondition:
        # * agent is not logged
        # * line has an extension
        interface = self._get_interface(agent)
        state_interface = self._get_state_interface_from_line_id(line_id)
        extension, context = self._line_dao.get_main_extension_context_from_line_id(
            line_id
        )
        self._do_login(agent, extension, context, interface, state_interface)

    def _do_login(self, agent, extension, context, interface, state_interface):
        self._update_agent_status(agent, extension, context, interface, state_interface)
        self._update_queue_log(agent, extension, context)
        self._update_asterisk(agent, interface, state_interface)
        self._update_blf(agent)
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

    def _get_state_interface_from_line_id(self, line_id):
        try:
            with db_utils.session_scope():
                return self._line_dao.get_interface_from_line_id(line_id)
        except LookupError:
            raise NoSuchLineError(line_id)

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

    def _update_blf(self, agent):
        for user_id in agent.user_ids:
            self._blf_manager.set_user_blf(
                user_id, 'agentstaticlogin', 'INUSE', '*{}'.format(agent.id)
            )
            self._blf_manager.set_user_blf(
                user_id, 'agentstaticlogin', 'INUSE', agent.number
            )
            self._blf_manager.set_user_blf(
                user_id, 'agentstaticlogoff', 'NOT_INUSE', '*{}'.format(agent.id)
            )
            self._blf_manager.set_user_blf(
                user_id, 'agentstaticlogoff', 'NOT_INUSE', agent.number
            )
            self._blf_manager.set_user_blf(
                user_id, 'agentstaticlogtoggle', 'INUSE', '*{}'.format(agent.id)
            )
            self._blf_manager.set_user_blf(
                user_id, 'agentstaticlogtoggle', 'INUSE', agent.number
            )

    def _send_bus_status_update(self, agent):
        status = AgentStatusUpdateEvent.STATUS_LOGGED_IN
        event = AgentStatusUpdateEvent(agent.id, status)
        logger.debug('Looking for users with agent id %s...', agent.id)
        with db_utils.session_scope():
            tenant_uuid = self._agent_dao.agent_with_id(agent.id).tenant_uuid
            users = self._user_dao.find_all_by_agent_id(agent.id)
            logger.debug('Found %s users.', len(users))
            headers = {
                'user_uuid:{uuid}'.format(uuid=user.uuid): True for user in users
            }
            headers['agent_id:{id}'.format(id=str(agent.id))] = True
            headers['tenant_uuid'] = tenant_uuid
            self._bus_publisher.publish(event, headers=headers)
