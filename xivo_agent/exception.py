# -*- coding: utf-8 -*-
# Copyright (C) 2012-2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

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
