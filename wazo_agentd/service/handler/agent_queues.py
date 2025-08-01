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
        self,
        user_uuid,
        tenant_uuids=None,
        order=None,
        direction=None,
        limit=None,
        offset=None,
    ):
        logger.info('Executing list_user_queues command (user %s)', user_uuid)
        with db_utils.session_scope():
            agent = self._agent_dao.get_agent_by_user_uuid(
                user_uuid, tenant_uuids=tenant_uuids
            )
        return self._handle_list_queues(agent, order, direction, limit, offset)

    @debug.trace_duration
    def handle_list_queues_by_number(
        self,
        agent_number,
        tenant_uuids=None,
        order=None,
        direction=None,
        limit=None,
        offset=None,
    ):
        logger.info('Executing list_queues_by_number command (agent %s)', agent_number)
        with db_utils.session_scope():
            agent = self._agent_dao.get_agent_by_number(
                agent_number, tenant_uuids=tenant_uuids
            )
        return self._handle_list_queues(agent, order, direction, limit, offset)

    @debug.trace_duration
    def handle_list_queues_by_id(
        self,
        agent_id,
        tenant_uuids=None,
        order=None,
        direction=None,
        limit=None,
        offset=None,
    ):
        logger.info('Executing list_queues command (agent %s)', agent_id)
        with db_utils.session_scope():
            agent = self._agent_dao.get_agent(agent_id, tenant_uuids=tenant_uuids)
        return self._handle_list_queues(agent, order, direction, limit, offset)

    def _handle_list_queues(
        self, agent, order=None, direction=None, limit=None, offset=None
    ):
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

        # Validate limit parameter
        if limit is not None and (not isinstance(limit, int) or limit < 0):
            raise ValueError("Invalid limit parameter: must be a non-negative integer")

        # Validate offset parameter
        if offset is not None and (not isinstance(offset, int) or offset < 0):
            raise ValueError("Invalid offset parameter: must be a non-negative integer")

        # Default values
        order = order or 'id'
        direction = direction or 'asc'
        limit = limit or 100
        offset = offset or 0

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

        # Apply pagination
        total_count = len(queues)
        start_index = min(offset, total_count)
        end_index = min(start_index + limit, total_count)
        paginated_queues = queues[start_index:end_index]

        return {
            'items': paginated_queues,
            'total': total_count,
            'filtered': len(paginated_queues),
        }
