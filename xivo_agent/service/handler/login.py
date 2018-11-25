# Copyright (C) 2013-2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

import logging

from xivo import debug
from xivo_dao.helpers import db_utils

logger = logging.getLogger(__name__)


class LoginHandler(object):

    def __init__(self, login_manager, agent_dao):
        self._login_manager = login_manager
        self._agent_dao = agent_dao

    @debug.trace_duration
    def handle_login_by_id(self, agent_id, extension, context):
        logger.info('Executing login command (ID %s) on %s@%s', agent_id, extension, context)
        with db_utils.session_scope():
            agent = self._agent_dao.get_agent(agent_id)
        self._handle_login(agent, extension, context)

    @debug.trace_duration
    def handle_login_by_number(self, agent_number, extension, context):
        logger.info('Executing login command (number %s) on %s@%s', agent_number, extension, context)
        with db_utils.session_scope():
            agent = self._agent_dao.get_agent_by_number(agent_number)
        self._handle_login(agent, extension, context)

    def _handle_login(self, agent, extension, context):
        self._login_manager.login_agent(agent, extension, context)
