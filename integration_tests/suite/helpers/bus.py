# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_test_helpers import bus as bus_helper


class BusClient(bus_helper.BusClient):
    def send_delete_queue_event(self, queue_id):
        self.publish(
            {'data': {'id': queue_id}, 'name': 'queue_deleted'}, 'config.queue.deleted'
        )
