# Copyright 2019-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_test_helpers import bus as bus_helper


class BusClient(bus_helper.BusClient):
    def send_delete_queue_event(self, queue_id):
        self.publish(
            {'data': {'id': queue_id}, 'name': 'queue_deleted'},
            headers={'name': 'queue_deleted'},
        )

    def send_queue_member_pause(
        self, agent_number, agent_id, paused=True, queue_name=''
    ):
        self.publish(
            {
                'data': {
                    'Paused': '1' if paused else '0',
                    'MemberName': f'local/{agent_number}',
                    'PausedReason': 'Eating potatoes',
                    'Queue': queue_name,
                    'Interface': f'Local/id-{agent_id}@agentcallback',
                },
                'name': 'QueueMemberPause',
            },
            headers={'name': 'QueueMemberPause'},
        )

    def send_agent_deleted_event(self, agent_id):
        self.publish(
            {'data': {'id': agent_id}, 'name': 'agent_deleted'},
            headers={'name': 'agent_deleted'},
            routing_key='config.agent.deleted',
        )
