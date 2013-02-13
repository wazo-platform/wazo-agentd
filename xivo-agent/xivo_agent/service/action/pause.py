# -*- coding: utf-8 -*-

# Copyright (C) 2013  Avencall
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


class PauseAction(object):

    def __init__(self, ami_client):
        self._ami_client = ami_client

    def pause_agent(self, agent_status):
        self._ami_client.queue_pause(agent_status.interface, '1')

    def unpause_agent(self, agent_status):
        self._ami_client.queue_pause(agent_status.interface, '0')
