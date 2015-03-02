# -*- coding: utf-8 -*-

# Copyright (C) 2012-2015 Avencall
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

from xivo_agent.resources.agent import error as error_messages
from xivo_agent.ctl.producer import BusProducerError


class AgentClientError(BusProducerError):
    # TODO remove once AgentClient has been all moved into xivo-agentd-client
    pass


class AgentServerError(Exception):

    error = 'server error'


class NoSuchAgentError(AgentServerError):

    error = error_messages.NO_SUCH_AGENT


class NoSuchExtensionError(AgentServerError):

    error = error_messages.NO_SUCH_EXTEN


class NoSuchQueueError(AgentServerError):

    error = error_messages.NO_SUCH_QUEUE


class AgentNotLoggedError(AgentServerError):

    error = error_messages.NOT_LOGGED


class AgentAlreadyLoggedError(AgentServerError):

    error = error_messages.ALREADY_LOGGED


class AgentNotInQueueError(AgentServerError):

    error = error_messages.NOT_IN_QUEUE


class AgentAlreadyInQueueError(AgentServerError):

    error = error_messages.ALREADY_IN_QUEUE


class ExtensionAlreadyInUseError(AgentServerError):

    error = error_messages.ALREADY_IN_USE
