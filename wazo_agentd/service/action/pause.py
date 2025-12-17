# Copyright 2013-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from wazo_amid_client.exceptions import AmidProtocolError

logger = logging.getLogger(__name__)


class PauseAction:
    def __init__(self, amid_client):
        self._amid_client = amid_client

    def pause_agent(self, agent_status, reason):
        if not any(queue.logged for queue in agent_status.queues):
            logger.debug(
                'agent %s has no active queues to pause', agent_status.agent_id
            )
            return

        try:
            self._amid_client.action(
                'QueuePause',
                {
                    'Queue': None,
                    'Interface': agent_status.interface,
                    'Paused': '1',
                    'Reason': reason,
                },
            )
        except AmidProtocolError as e:
            logger.warning('Failed to pause agent %s: %s', agent_status.agent_id, e)

    def unpause_agent(self, agent_status):
        if not any(queue.logged for queue in agent_status.queues):
            logger.debug(
                'agent %s has no active queues to unpause', agent_status.agent_id
            )
            return

        try:
            self._amid_client.action(
                'QueuePause',
                {
                    'Queue': None,
                    'Interface': agent_status.interface,
                    'Paused': '0',
                    'Reason': None,
                },
            )
        except AmidProtocolError as e:
            logger.warning('Failed to unpause agent %s: %s', agent_status.agent_id, e)
