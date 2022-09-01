# Copyright 2015-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo.status import Status
from xivo_bus.consumer import BusConsumer as BaseConsumer
from xivo_bus.publisher import BusPublisherWithQueue as BasePublisher
from xivo_bus.resources.ami.event import AMIEvent


class BusConsumer(BaseConsumer):
    def provide_status(self, status):
        status['bus_consumer']['status'] = Status.ok if self.is_running else Status.fail


class BusPublisherWithQueue(BasePublisher):
    def provide_status(self, status):
        status['bus_publisher']['status'] = (
            Status.ok if self.is_running else Status.fail
        )


class AgentPauseEvent(AMIEvent):
    name = 'QueueMemberPause'
    routing_key = 'ami.{}'.format(name)
