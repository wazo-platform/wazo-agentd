# -*- coding: UTF-8 -*-

from xivo_agent.ctl import error


class GetInterfaceForExtensionStep(object):

    def __init__(self, linefeatures_dao):
        self._linefeatures_dao = linefeatures_dao

    def execute(self, command, response, blackboard):
        try:
            blackboard.interface = self._linefeatures_dao.get_interface_from_exten_and_context(blackboard.extension, blackboard.context)
        except LookupError:
            response.error = error.NO_SUCH_EXTEN
