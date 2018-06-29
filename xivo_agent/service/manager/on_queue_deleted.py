# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers import db_utils


class OnQueueDeletedManager(object):

    def __init__(self, agent_status_dao):
        self._agent_status_dao = agent_status_dao

    def on_queue_deleted(self, queue_id):
        with db_utils.session_scope():
            self._agent_status_dao.remove_all_agents_from_queue(queue_id)
