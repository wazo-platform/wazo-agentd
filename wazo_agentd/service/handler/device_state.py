# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from xivo import debug
from xivo_dao.helpers import db_utils

logger = logging.getLogger(__name__)


class DeviceStateHandler:
    def __init__(self, agent_status_dao, logoff_manager):
        self._agent_status_dao = agent_status_dao
        self._logoff_manager = logoff_manager

    @debug.trace_duration
    def handle_on_device_state_updated(self, msg):
        if msg['State'] == 'UNAVAILABLE':
            with db_utils.session_scope():
                device = msg['Device']
                agent_status = self._agent_status_dao.get_status_by_state_interface(device)
                if agent_status:
                    logger.info(
                        'Executing logoff command (agent %s)', agent_status.agent_number
                    )
                    self._logoff_manager.logoff_agent(agent_status)
