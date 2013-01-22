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

from xivo_agent.ctl import error


class GetInterfaceStep(object):

    _INTERFACE = 'Local/id-{0}@agentcallback'

    def execute(self, command, response, blackboard):
        blackboard.interface = self._build_interface(blackboard.agent.id)

    def _build_interface(self, agent_id):
        return self._INTERFACE.format(agent_id)


class GetStateInterfaceForExtensionStep(object):

    def __init__(self, line_dao):
        self._line_dao = line_dao

    def execute(self, command, response, blackboard):
        try:
            blackboard.state_interface = self._line_dao.get_interface_from_exten_and_context(blackboard.extension, blackboard.context)
        except LookupError:
            response.error = error.NO_SUCH_EXTEN
