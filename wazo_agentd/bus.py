# Copyright 2015-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.ami.event import AMIEvent


class AgentPauseEvent(AMIEvent):
    name = 'QueueMemberPause'
    routing_key = 'ami.{}'.format(name)
