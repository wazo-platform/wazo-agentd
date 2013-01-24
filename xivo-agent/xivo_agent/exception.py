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

from xivo_agent.ctl import error


class AgentClientError(Exception):

    def __init__(self, error):
        Exception.__init__(self, error)
        self.error = error


class AgentServerError(Exception):

    error = error.SERVER_ERROR


class NoSuchAgentError(AgentServerError):

    error = error.NO_SUCH_AGENT


class NoSuchExtensionError(AgentServerError):

    error = error.NO_SUCH_EXTEN


class NoSuchQueueError(AgentServerError):

    error = error.NO_SUCH_QUEUE


class AgentNotLoggedError(AgentServerError):

    error = error.NOT_LOGGED


class AgentAlreadyLoggedError(AgentServerError):

    error = error.ALREADY_LOGGED


class AgentNotInQueueError(AgentServerError):

    error = error.NOT_IN_QUEUE


class AgentAlreadyInQueueError(AgentServerError):

    error = error.ALREADY_IN_QUEUE


class ExtensionAlreadyInUseError(AgentServerError):

    error = error.ALREADY_IN_USE
