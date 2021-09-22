# Copyright 2012-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

# The following strings are part of the exposed HTTP API; don't rename them
# or you'll break the API.
NO_SUCH_AGENT = 'no such agent'
NO_SUCH_LINE = 'no such line'
NO_SUCH_QUEUE = 'no such queue'
ALREADY_LOGGED = 'already logged'
NOT_LOGGED = 'not logged in'
ALREADY_IN_USE = 'extension and context already in use'
ALREADY_IN_QUEUE = 'agent already in queue'
NOT_IN_QUEUE = 'agent not in queue'
NO_SUCH_EXTEN = 'no such extension and context'
CONTEXT_DIFFERENT_TENANT = 'agent and context are not in the same tenant'
QUEUE_DIFFERENT_TENANT = 'agent and queue are not in the same tenant'


class AgentServerError(Exception):

    error = 'server error'


class NoSuchAgentError(AgentServerError):

    error = NO_SUCH_AGENT


class NoSuchExtensionError(AgentServerError):

    error = NO_SUCH_EXTEN


class NoSuchLineError(AgentServerError):

    error = NO_SUCH_LINE


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


class ContextDifferentTenantError(AgentServerError):

    error = CONTEXT_DIFFERENT_TENANT


class QueueDifferentTenantError(AgentServerError):

    error = QUEUE_DIFFERENT_TENANT


class NoSuchExtenFeatureError(Exception):
    pass
