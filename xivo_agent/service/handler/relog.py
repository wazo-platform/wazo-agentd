# -*- coding: utf-8 -*-
# Copyright (C) 2013-2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

import logging
from xivo import debug

logger = logging.getLogger(__name__)


class RelogHandler(object):

    def __init__(self, relog_manager):
        self._relog_manager = relog_manager

    @debug.trace_duration
    def handle_relog_all(self):
        logger.info('Executing relog all command')
        self._relog_manager.relog_all_agents()
