# -*- coding: utf-8 -*-

# Copyright (C) 2012-2013 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from __future__ import unicode_literals

from xivo_agent.ctl.commands.abstract import AbstractAgentCommand


class StatusCommand(AbstractAgentCommand):

    name = 'status'

    def marshal(self):
        return {
            'agent_id': self.agent_id,
            'agent_number': self.agent_number,
        }

    @classmethod
    def unmarshal(cls, msg):
        cmd = cls()
        cmd._set_agent_id_and_number(msg['agent_id'], msg['agent_number'])
        return cmd
