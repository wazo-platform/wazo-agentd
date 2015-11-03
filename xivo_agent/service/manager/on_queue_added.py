# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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

from xivo_dao.helpers import db_utils


class OnQueueAddedManager(object):

    def __init__(self, add_to_queue_action, agent_status_dao):
        self._add_to_queue_action = add_to_queue_action
        self._agent_status_dao = agent_status_dao

    def on_queue_added(self, queue):
        with db_utils.session_scope():
            agent_statuses = self._agent_status_dao.get_statuses_for_queue(queue.id)
        for agent_status in agent_statuses:
            self._add_to_queue_action.add_agent_to_queue(agent_status, queue)
