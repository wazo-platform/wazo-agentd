# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from xivo import debug
from xivo_dao.helpers import db_utils

logger = logging.getLogger(__name__)


class AgentQueuesHandler:
    def __init__(self, agent_dao):
        self._agent_dao = agent_dao

    @debug.trace_duration
    def handle_list_user_queues(
        self, user_uuid, tenant_uuids=None, order=None, direction=None
    ):
        logger.info('Executing list_user_queues command (user %s)', user_uuid)
        with db_utils.session_scope():
            agent = self._agent_dao.get_agent_by_user_uuid(
                user_uuid, tenant_uuids=tenant_uuids
            )
        return self._handle_list_queues(agent, order, direction)

    @debug.trace_duration
    def handle_list_queues_by_number(
        self, agent_number, tenant_uuids=None, order=None, direction=None
    ):
        logger.info('Executing list_queues_by_number command (agent %s)', agent_number)
        with db_utils.session_scope():
            agent = self._agent_dao.get_agent_by_number(
                agent_number, tenant_uuids=tenant_uuids
            )
        return self._handle_list_queues(agent, order, direction)

    @debug.trace_duration
    def handle_list_queues_by_id(
        self, agent_id, tenant_uuids=None, order=None, direction=None
    ):
        logger.info('Executing list_queues command (agent %s)', agent_id)
        with db_utils.session_scope():
            agent = self._agent_dao.get_agent(agent_id, tenant_uuids=tenant_uuids)
        return self._handle_list_queues(agent, order, direction)

    def _handle_list_queues(self, agent, order=None, direction=None):
        # Validate order parameter
        valid_orders = ['id', 'name', 'display_name']
        if order is not None and order not in valid_orders:
            raise ValueError(
                f"Invalid order parameter: {order}. Valid values are: {valid_orders}"
            )

        # Validate direction parameter
        valid_directions = ['asc', 'desc']
        if direction is not None and direction not in valid_directions:
            raise ValueError(
                f"Invalid direction parameter: {direction}. Valid values are: {valid_directions}"
            )

        # Default values
        order = order or 'id'
        direction = direction or 'asc'

        queues = [
            {
                'id': queue.id,
                'name': queue.name,
                'display_name': queue.label,
            }
            for queue in agent.queues
        ]

        # Sort the queues based on order and direction
        reverse = direction == 'desc'
        if order == 'id':
            queues.sort(key=lambda x: x['id'], reverse=reverse)
        elif order == 'name':
            queues.sort(key=lambda x: x['name'], reverse=reverse)
        elif order == 'display_name':
            queues.sort(key=lambda x: x['display_name'], reverse=reverse)

        queue_count = len(queues)
        return {
            'items': queues,
            'total': queue_count,
            'filtered': queue_count,
        }
