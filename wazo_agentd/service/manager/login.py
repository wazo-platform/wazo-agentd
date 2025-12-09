# Copyright 2013-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from xivo_dao.helpers import db_utils

from wazo_agentd.exception import (
    AgentAlreadyLoggedError,
    ContextDifferentTenantError,
    ExtensionAlreadyInUseError,
    NoSuchExtensionError,
    NoSuchLineError,
)

logger = logging.getLogger(__name__)


class LoginManager:
    def __init__(self, login_action, agent_status_dao, context_dao, line_dao):
        self._login_action = login_action
        self._agent_status_dao = agent_status_dao
        self._line_dao = line_dao
        self._context_dao = context_dao

    def login_agent(self, agent, extension, context, endpoint=None):
        self._check_context_is_in_same_tenant(agent, context)
        self._check_agent_is_not_logged(agent)
        self._check_extension_is_not_in_use(extension, context)
        if endpoint:
            self._check_endpoint_valid_for_exten_and_context(
                endpoint, extension, context
            )
        self._login_action.login_agent(agent, extension, context, endpoint)

    def login_user_agent(self, agent, user_uuid, line_id):
        self._check_agent_is_not_logged(agent)
        self._check_user_owns_line(user_uuid, line_id)
        self._login_action.login_agent_on_line(agent, line_id)

    def _check_context_is_in_same_tenant(self, agent, context):
        with db_utils.session_scope():
            retrieved_context = self._context_dao.get(context)
            if not retrieved_context:
                raise NoSuchExtensionError()

            context_tenant_uuid = retrieved_context.tenant_uuid
            if agent.tenant_uuid != context_tenant_uuid:
                raise ContextDifferentTenantError()

    def _check_agent_is_not_logged(self, agent):
        with db_utils.session_scope():
            agent_status = self._agent_status_dao.get_status(agent.id)
        if agent_status is not None:
            raise AgentAlreadyLoggedError()

    def _check_extension_is_not_in_use(self, extension, context):
        with db_utils.session_scope():
            if self._agent_status_dao.is_extension_in_use(extension, context):
                raise ExtensionAlreadyInUseError()

    def _check_user_owns_line(self, user_uuid, line_id):
        with db_utils.session_scope():
            if not self._line_dao.is_line_owned_by_user(user_uuid, line_id):
                raise NoSuchLineError()

    def _check_endpoint_valid_for_exten_and_context(self, endpoint, extension, context):
        with db_utils.session_scope():
            try:
                interfaces = self._line_dao.get_interfaces_from_exten_and_context(
                    extension, context
                )
            except LookupError:
                raise NoSuchExtensionError(extension, context)

            if endpoint not in interfaces:
                raise NoSuchExtensionError(extension, context)
