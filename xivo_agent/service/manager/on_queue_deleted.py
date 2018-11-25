# Copyright 2013-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers import db_utils


class OnQueueDeletedManager:

    def __init__(self, agent_status_dao):
        self._agent_status_dao = agent_status_dao

    def on_queue_deleted(self, queue_id):
        with db_utils.session_scope():
            self._agent_status_dao.remove_all_agents_from_queue(queue_id)
