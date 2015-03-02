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

# The following strings are part of the exposed HTTP API; don't rename them
# or you'll break the API.
NO_SUCH_AGENT = 'no such agent'
NO_SUCH_QUEUE = 'no such queue'
ALREADY_LOGGED = 'already logged'
NOT_LOGGED = 'not logged in'
ALREADY_IN_USE = 'extension and context already in use'
ALREADY_IN_QUEUE = 'agent already in queue'
NOT_IN_QUEUE = 'agent not in queue'
NO_SUCH_EXTEN = 'no such extension and context'


class AgentServerError(Exception):

    error = 'server error'


class NoSuchAgentError(AgentServerError):

    error = NO_SUCH_AGENT


class NoSuchExtensionError(AgentServerError):

    error = NO_SUCH_EXTEN


class NoSuchQueueError(AgentServerError):

    error = NO_SUCH_QUEUE


class AgentNotLoggedError(AgentServerError):

    error = NOT_LOGGED


class AgentAlreadyLoggedError(AgentServerError):

    error = ALREADY_LOGGED


class AgentNotInQueueError(AgentServerError):

    error = NOT_IN_QUEUE


class AgentAlreadyInQueueError(AgentServerError):

    error = ALREADY_IN_QUEUE


class ExtensionAlreadyInUseError(AgentServerError):

    error = ALREADY_IN_USE
