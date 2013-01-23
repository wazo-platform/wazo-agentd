# -*- coding: utf-8 -*-

# Copyright (C) 2012-2013 Avencall
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

import logging
from xivo_agent.ctl import commands
from xivo_agent.service.blackboard import Blackboard
from xivo_agent.service.manager.on_agent_deleted import OnAgentDeletedManager
from xivo_agent.service.manager.on_agent_updated import OnAgentUpdatedManager
from xivo_agent.service.manager.on_queue_added import OnQueueAddedManager
from xivo_agent.service.manager.on_queue_deleted import OnQueueDeletedManager
from xivo_agent.service.manager.on_queue_updated import OnQueueUpdatedManager

logger = logging.getLogger(__name__)


class AgentService(object):

    def __init__(self, agent_server):
        self._agent_server = agent_server
        self._steps = {}

    def init(self, step_factory):
        self._add_login_cmd(step_factory)
        self._add_logoff_cmd(step_factory)
        self._add_logoff_all_cmd(step_factory)
        self._add_add_to_queue_cmd(step_factory)
        self._add_remove_from_queue_cmd(step_factory)
        self._add_status_cmd(step_factory)
        self._add_statuses_cmd(step_factory)
        self._add_on_agent_updated_cmd(step_factory)
        self._add_on_agent_deleted_cmd(step_factory)
        self._add_on_queue_added_cmd(step_factory)
        self._add_on_queue_updated_cmd(step_factory)
        self._add_on_queue_deleted_cmd(step_factory)
        self._add_ping_cmd()

    def run(self):
        self._agent_server.run()

    def _add_login_cmd(self, step_factory):
        steps = [
            step_factory.get_agent(),
            step_factory.get_agent_status(),
            step_factory.check_agent_is_not_logged(),
            step_factory.check_extension_is_not_in_use(),
            step_factory.get_interface(),
            step_factory.get_state_interface_for_extension(),
            step_factory.update_agent_status(),
            step_factory.update_queue_log(),
            step_factory.add_agent_to_queues(),
            step_factory.send_agent_login_event(),
        ]
        self._add_cmd(commands.LoginCommand, self._exec_login_cmd, steps)

    def _add_logoff_cmd(self, step_factory):
        steps = [
            step_factory.get_agent(),
            step_factory.get_agent_status(),
            step_factory.check_agent_is_logged(),
            step_factory.send_agent_logoff_event(),
            step_factory.remove_agent_from_queues(),
            step_factory.update_queue_log(),
            step_factory.update_agent_status(),
        ]
        self._add_cmd(commands.LogoffCommand, self._exec_logoff_cmd, steps)

    def _add_logoff_all_cmd(self, step_factory):
        steps = [
            step_factory.get_logged_in_agents(),
            step_factory.logoff_all_agents()
        ]
        self._add_cmd(commands.LogoffAllCommand, self._exec_logoff_all_cmd, steps)

    def _add_add_to_queue_cmd(self, step_factory):
        steps = [
            step_factory.get_agent(),
            step_factory.get_agent_status(),
            step_factory.get_queue(),
            step_factory.check_agent_is_not_member_of_queue(),
            step_factory.insert_agent_into_queuemember(),
            step_factory.send_agent_added_to_queue_event(),
            step_factory.add_agent_to_queue(),
            step_factory.update_agent_status(),
        ]
        self._add_cmd(commands.AddToQueueCommand, self._exec_add_to_queue_cmd, steps)

    def _add_remove_from_queue_cmd(self, step_factory):
        steps = [
            step_factory.get_agent(),
            step_factory.get_agent_status(),
            step_factory.get_queue(),
            step_factory.check_agent_is_member_of_queue(),
            step_factory.delete_agent_from_queuemember(),
            step_factory.send_agent_removed_from_queue_event(),
            step_factory.remove_agent_from_queue(),
            step_factory.update_agent_status(),
        ]
        self._add_cmd(commands.RemoveFromQueueCommand, self._exec_remove_from_queue_cmd, steps)

    def _add_status_cmd(self, step_factory):
        steps = [
            step_factory.get_agent(),
            step_factory.get_agent_status(),
        ]
        self._add_cmd(commands.StatusCommand, self._exec_status_cmd, steps)

    def _add_statuses_cmd(self, step_factory):
        steps = [
            step_factory.get_agent_statuses(),
        ]
        self._add_cmd(commands.StatusesCommand, self._exec_statuses_cmd, steps)

    def _add_on_agent_updated_cmd(self, step_factory):
        self._on_agent_updated_manager = OnAgentUpdatedManager(step_factory)
        self._agent_server.add_command(commands.OnAgentUpdatedCommand, self._exec_on_agent_updated_cmd)

    def _add_on_agent_deleted_cmd(self, step_factory):
        self._on_agent_deleted_manager = OnAgentDeletedManager(step_factory)
        self._agent_server.add_command(commands.OnAgentDeletedCommand, self._exec_on_agent_deleted_cmd)

    def _add_on_queue_added_cmd(self, step_factory):
        self._on_queue_added_manager = OnQueueAddedManager(step_factory)
        self._agent_server.add_command(commands.OnQueueAddedCommand, self._exec_on_queue_added_cmd)

    def _add_on_queue_updated_cmd(self, step_factory):
        self._on_queue_updated_manager = OnQueueUpdatedManager(step_factory)
        self._agent_server.add_command(commands.OnQueueUpdatedCommand, self._exec_on_queue_updated_cmd)

    def _add_on_queue_deleted_cmd(self, step_factory):
        self._on_queue_deleted_manager = OnQueueDeletedManager(step_factory)
        self._agent_server.add_command(commands.OnQueueDeletedCommand, self._exec_on_queue_deleted_cmd)

    def _add_ping_cmd(self):
        self._agent_server.add_command(commands.PingCommand, self._exec_ping_cmd)

    def _add_cmd(self, cmd_class, callback, steps):
        self._steps[cmd_class.name] = steps
        self._agent_server.add_command(cmd_class, callback)

    def _exec_login_cmd(self, login_cmd, response):
        logger.info('Executing login command (ID %s, number %s) on %s@%s', login_cmd.agent_id, login_cmd.agent_number, login_cmd.extension, login_cmd.context)
        blackboard = Blackboard()
        blackboard.extension = login_cmd.extension
        blackboard.context = login_cmd.context

        self._exec_cmd(login_cmd, response, blackboard)

    def _exec_logoff_cmd(self, logoff_cmd, response):
        logger.info('Executing logoff command (ID %s, number %s)', logoff_cmd.agent_id, logoff_cmd.agent_number)
        blackboard = Blackboard()

        self._exec_cmd(logoff_cmd, response, blackboard)

    def _exec_logoff_all_cmd(self, logoff_all_cmd, response):
        logger.info('Executing logoff_all command')
        blackboard = Blackboard()

        self._exec_cmd(logoff_all_cmd, response, blackboard)

    def _exec_add_to_queue_cmd(self, add_to_queue_cmd, response):
        logger.info('Executing add to queue command (ID %s)', add_to_queue_cmd.agent_id)
        blackboard = Blackboard()

        self._exec_cmd(add_to_queue_cmd, response, blackboard)

    def _exec_remove_from_queue_cmd(self, remove_from_queue_cmd, response):
        logger.info('Executing remove from queue command (ID %s)', remove_from_queue_cmd.agent_id)
        blackboard = Blackboard()

        self._exec_cmd(remove_from_queue_cmd, response, blackboard)

    def _exec_status_cmd(self, status_cmd, response):
        logger.info('Executing status command (ID %s, number %s)', status_cmd.agent_id, status_cmd.agent_number)
        blackboard = Blackboard()

        self._exec_cmd(status_cmd, response, blackboard)

        if not response.error:
            status = blackboard.agent_status
            if status is None:
                logged = False
                extension = None
                context = None
            else:
                logged = True
                extension = status.extension
                context = status.context
            response.value = {
                'id': blackboard.agent.id,
                'number': blackboard.agent.number,
                'logged': logged,
                'extension': extension,
                'context': context,
            }

    def _exec_statuses_cmd(self, statuses_cmd, response):
        logger.info('Executing statuses command')
        blackboard = Blackboard()

        self._exec_cmd(statuses_cmd, response, blackboard)

        response.value = [
            {'id': status.agent_id,
             'number': status.agent_number,
             'logged': status.logged,
             'extension': status.extension,
             'context': status.context}
            for status in blackboard.agent_statuses
        ]

    def _exec_on_agent_updated_cmd(self, on_agent_updated_cmd, response):
        logger.info('Executing on agent updated command (ID %s)', on_agent_updated_cmd.agent_id)

        agent_id = on_agent_updated_cmd.agent_id
        self._on_agent_updated_manager.on_agent_updated(agent_id)

    def _exec_on_agent_deleted_cmd(self, on_agent_deleted_cmd, response):
        logger.info('Executing on agent deleted command (ID %s)', on_agent_deleted_cmd.agent_id)

        agent_id = on_agent_deleted_cmd.agent_id
        self._on_agent_deleted_manager.on_agent_deleted(agent_id)

    def _exec_on_queue_added_cmd(self, on_queue_added_cmd, response):
        logger.info('Executing on queue added command (ID %s)', on_queue_added_cmd.queue_id)

        queue_id = on_queue_added_cmd.queue_id
        self._on_queue_added_manager.on_queue_added(queue_id)

    def _exec_on_queue_updated_cmd(self, on_queue_updated_cmd, response):
        logger.info('Executing on queue updated command (ID %s)', on_queue_updated_cmd.queue_id)

        queue_id = on_queue_updated_cmd.queue_id
        self._on_queue_updated_manager.on_queue_updated(queue_id)

    def _exec_on_queue_deleted_cmd(self, on_queue_deleted_cmd, response):
        logger.info('Executing on queue deleted command (ID %s)', on_queue_deleted_cmd.queue_id)

        queue_id = on_queue_deleted_cmd.queue_id
        self._on_queue_deleted_manager.on_queue_deleted(queue_id)

    def _exec_ping_cmd(self, ping_cmd, response):
        response.value = 'pong'

    def _exec_cmd(self, cmd, response, blackboard):
        steps = self._steps[cmd.name]
        for step in steps:
            logger.debug('Executing step %s', step)
            step.execute(cmd, response, blackboard)
            if response.error:
                logger.debug('Step %s returned error %s', step, response.error)
                break
