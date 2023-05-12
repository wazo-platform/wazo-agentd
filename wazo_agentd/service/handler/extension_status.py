# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from xivo import debug
from xivo_dao.helpers import db_utils

from wazo_agentd.exception import AgentNotLoggedError

logger = logging.getLogger(__name__)


class ExtensionStatusHandler:
    def __init__(self, agent_status_dao, user_dao, logoff_manager):
        self._agent_status_dao = agent_status_dao
        self._user_dao = user_dao
        self._logoff_manager = logoff_manager

    @debug.trace_duration
    def handle_on_extension_status_updated(self, msg):
        if msg['StatusText'] == 'Unavailable' and msg['Context'] != 'usersharedlines':
            with db_utils.session_scope():
                try:
                    user = self._user_dao.get_user_by_number_context(
                        msg['Exten'], msg['Context']
                    )
                    self.handle_logoff_user_agent(
                        user.uuid, tenant_uuids=[user.tenant_uuid]
                    )
                except (LookupError, AgentNotLoggedError) as e:
                    logger.debug(f'Cannot logout agent for user {user.uuid}, '
                                 f'{msg["Exten"]}@{msg["Context"]} ({e})')

    @debug.trace_duration
    def handle_logoff_user_agent(self, user_uuid, tenant_uuids=None):
        with db_utils.session_scope():
            agent_status = self._agent_status_dao.get_status_by_user(
                user_uuid, tenant_uuids=tenant_uuids
            )
            if agent_status:
                logger.info('Executing logoff command (agent of user %s)', user_uuid)
                self._logoff_manager.logoff_agent(agent_status)
