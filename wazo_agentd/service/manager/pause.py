# Copyright 2013-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_agentd.exception import AgentNotLoggedError, NoSuchAgentError
from xivo_dao.helpers import db_utils


class PauseManager:
    def __init__(self, pause_action, agent_dao):
        self._agent_dao = agent_dao
        self._pause_action = pause_action

    def pause_agent(self, agent_status, reason):
        self._check_agent_is_logged(agent_status)
        self._pause_action.pause_agent(agent_status, reason)

    def pause_user_agent(self, user_uuid, agent_status, reason, tenant_uuids=None):
        self._check_user_has_agent(user_uuid, tenant_uuids)
        self._check_agent_is_logged(agent_status)
        self._pause_action.pause_agent(agent_status, reason)

    def unpause_agent(self, agent_status):
        self._check_agent_is_logged(agent_status)
        self._pause_action.unpause_agent(agent_status)

    def resume_user_agent(self, user_uuid, agent_status, tenant_uuids=None):
        self._check_user_has_agent(user_uuid, tenant_uuids)
        self._check_agent_is_logged(agent_status)
        self._pause_action.unpause_agent(agent_status)

    def _check_agent_is_logged(self, agent_status):
        if agent_status is None:
            raise AgentNotLoggedError()

    def _check_user_has_agent(self, user_uuid, tenant_uuids=None):
        try:
            with db_utils.session_scope():
                self._agent_dao.agent_with_user_uuid(
                    user_uuid, tenant_uuids=tenant_uuids
                )
        except LookupError:
            raise NoSuchAgentError()
