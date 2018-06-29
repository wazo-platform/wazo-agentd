# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers import db_utils


class RemoveFromQueueAction(object):

    def __init__(self, ami_client, agent_status_dao):
        self._ami_client = ami_client
        self._agent_status_dao = agent_status_dao

    def remove_agent_from_queue(self, agent_status, queue):
        self._update_asterisk(agent_status, queue)
        self._update_agent_status(agent_status, queue)

    def _update_asterisk(self, agent_status, queue):
        self._ami_client.queue_remove(queue.name, agent_status.interface)

    def _update_agent_status(self, agent_status, queue):
        with db_utils.session_scope():
            self._agent_status_dao.remove_agent_from_queues(agent_status.agent_id, [queue.id])
