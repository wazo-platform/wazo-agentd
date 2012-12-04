# -*- coding: UTF-8 -*-

# Copyright (C) 2012  Avencall
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

from xivo_agent.service import steps


class StepFactory(object):

    def __init__(self, ami_client, queue_log_manager, agent_login_dao, agentfeatures_dao, linefeatures_dao):
        self._ami_client = ami_client
        self._queue_log_manager = queue_log_manager
        self._agent_login_dao = agent_login_dao
        self._agentfeatures_dao = agentfeatures_dao
        self._linefeatures_dao = linefeatures_dao

    def get_agent(self):
        return steps.GetAgentStep(self._agentfeatures_dao)

    def get_agent_status(self):
        return steps.GetAgentStatusStep(self._agent_login_dao)

    def get_agent_statuses(self):
        return steps.GetAgentStatusesStep(self._agent_login_dao)

    def check_agent_is_logged(self):
        return steps.CheckAgentIsLoggedStep()

    def check_agent_is_not_logged(self):
        return steps.CheckAgentIsNotLoggedStep()

    def check_extension_is_not_in_use(self):
        return steps.CheckExtensionIsNotInUseStep(self._agent_login_dao)

    def get_interface_for_extension(self):
        return steps.GetInterfaceForExtensionStep(self._linefeatures_dao)

    def update_agent_status(self):
        return steps.UpdateAgentStatusStep(self._agent_login_dao)

    def update_queue_log(self):
        return steps.UpdateQueueLogStep(self._queue_log_manager)

    def add_agent_to_queues(self):
        return steps.AddAgentsToQueuesStep(self._ami_client)

    def remove_agent_from_queues(self):
        return steps.RemoveAgentsFromQueuesStep(self._ami_client)

    def send_agent_login_event(self):
        return steps.SendAgentLoginEventStep(self._ami_client)

    def send_agent_logoff_event(self):
        return steps.SendAgentLogoffEventStep(self._ami_client)
