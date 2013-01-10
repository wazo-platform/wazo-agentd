# -*- coding: UTF-8 -*-

# Copyright (C) 2012-2013  Avencall
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

    def __init__(self, ami_client, queue_log_manager, agent_status_dao, agent_dao,
                 line_dao, queue_dao, queue_member_dao):
        self._ami_client = ami_client
        self._queue_log_manager = queue_log_manager
        self._agent_status_dao = agent_status_dao
        self._agent_dao = agent_dao
        self._line_dao = line_dao
        self._queue_dao = queue_dao
        self._queue_member_dao = queue_member_dao

    def get_agent(self):
        return steps.GetAgentStep(self._agent_dao)

    def get_agent_status(self):
        return steps.GetAgentStatusStep(self._agent_status_dao)

    def get_agent_statuses(self):
        return steps.GetAgentStatusesStep(self._agent_status_dao)

    def get_queue(self):
        return steps.GetQueueStep(self._queue_dao)

    def check_agent_is_logged(self):
        return steps.CheckAgentIsLoggedStep()

    def check_agent_is_not_logged(self):
        return steps.CheckAgentIsNotLoggedStep()

    def check_agent_is_member_of_queue(self):
        return steps.CheckAgentIsMemberOfQueueStep()

    def check_agent_is_not_member_of_queue(self):
        return steps.CheckAgentIsNotMemberOfQueueStep()

    def check_extension_is_not_in_use(self):
        return steps.CheckExtensionIsNotInUseStep(self._agent_status_dao)

    def get_interface(self):
        return steps.GetInterfaceStep()

    def get_state_interface_for_extension(self):
        return steps.GetStateInterfaceForExtensionStep(self._line_dao)

    def insert_agent_into_queuemember(self):
        return steps.InsertAgentIntoQueuememberStep(self._queue_member_dao)

    def delete_agent_from_queuemember(self):
        return steps.DeleteAgentFromQueuememberStep(self._queue_member_dao)

    def update_agent_status(self):
        return steps.UpdateAgentStatusStep(self._agent_status_dao)

    def update_queue_log(self):
        return steps.UpdateQueueLogStep(self._queue_log_manager)

    def add_agent_to_queue(self):
        return steps.AddAgentToQueueStep(self._ami_client)

    def add_agent_to_queues(self):
        return steps.AddAgentToQueuesStep(self._ami_client)

    def remove_agent_from_queue(self):
        return steps.RemoveAgentFromQueueStep(self._ami_client)

    def remove_agent_from_queues(self):
        return steps.RemoveAgentFromQueuesStep(self._ami_client)

    def send_agent_added_to_queue_event(self):
        return steps.SendAgentAddedToQueueEventStep(self._ami_client)

    def send_agent_removed_from_queue_event(self):
        return steps.SendAgentRemovedFromQueueEventStep(self._ami_client)

    def send_agent_login_event(self):
        return steps.SendAgentLoginEventStep(self._ami_client)

    def send_agent_logoff_event(self):
        return steps.SendAgentLogoffEventStep(self._ami_client)

    def get_logged_in_agents(self):
        return steps.GetLoggedInAgentsStep(self._agent_status_dao, self._agent_dao)

    def logoff_all_agents(self):
        return steps.LogoffAllAgentsStep(
            self.remove_agent_from_queues(),
            self.update_queue_log(),
            self.update_agent_status(),
            self.send_agent_logoff_event()
        )
