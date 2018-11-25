# Copyright (C) 2013-2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

import logging

from xivo import debug
from xivo_dao.helpers import db_utils

logger = logging.getLogger(__name__)


class OnAgentHandler(object):

    def __init__(self, on_agent_deleted_manager, on_agent_updated_manager, agent_dao):
        self._on_agent_deleted_manager = on_agent_deleted_manager
        self._on_agent_updated_manager = on_agent_updated_manager
        self._agent_dao = agent_dao

    @debug.trace_duration
    def handle_on_agent_updated(self, agent_id):
        logger.info('Executing on agent updated command (ID %s)', agent_id)
        with db_utils.session_scope():
            agent = self._agent_dao.get_agent(agent_id)
        self._on_agent_updated_manager.on_agent_updated(agent)

    @debug.trace_duration
    def handle_on_agent_deleted(self, agent_id):
        logger.info('Executing on agent deleted command (ID %s)', agent_id)
        self._on_agent_deleted_manager.on_agent_deleted(agent_id)
