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

from __future__ import unicode_literals

from xivo_agent.command import abstract


class AddToQueueCommand(abstract.AbstractAgentAndQueueIDCommand):

    name = 'add_to_queue'


class LogoffByIDCommand(abstract.AbstractAgentIDCommand):

    name = 'logoff_by_id'


class LogoffByNumberCommand(abstract.AbstractAgentNumberCommand):

    name = 'logoff_by_number'


class LogoffAllCommand(abstract.AbstractNoDataCommand):

    name = 'logoff_all'


class RelogAllCommand(abstract.AbstractNoDataCommand):

    name = 'relog_all'


class OnAgentDeletedCommand(abstract.AbstractAgentIDCommand):

    name = 'on_agent_deleted'


class OnAgentUpdatedCommand(abstract.AbstractAgentIDCommand):

    name = 'on_agent_updated'


class OnQueueAddedCommand(abstract.AbstractQueueIDCommand):

    name = 'on_queue_added'


class OnQueueDeletedCommand(abstract.AbstractQueueIDCommand):

    name = 'on_queue_deleted'


class OnQueueUpdatedCommand(abstract.AbstractQueueIDCommand):

    name = 'on_queue_updated'


class PingCommand(abstract.AbstractNoDataCommand):

    name = 'ping'


class RemoveFromQueueCommand(abstract.AbstractAgentAndQueueIDCommand):

    name = 'remove_from_queue'


class StatusByIDCommand(abstract.AbstractAgentIDCommand):

    name = 'status_by_id'


class StatusByNumberCommand(abstract.AbstractAgentNumberCommand):

    name = 'status_by_number'


class StatusesCommand(abstract.AbstractNoDataCommand):

    name = 'statuses'
