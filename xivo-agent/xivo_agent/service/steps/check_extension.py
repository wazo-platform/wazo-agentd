# -*- coding: UTF-8 -*-

from xivo_agent.ctl import error


class CheckExtensionIsNotInUseStep(object):

    def __init__(self, agent_login_dao):
        self._agent_login_dao = agent_login_dao

    def execute(self, command, response, blackboard):
        if self._agent_login_dao.is_extension_in_use(blackboard.extension, blackboard.context):
            response.error = error.ALREADY_IN_USE
