# -*- coding: UTF-8 -*-

from xivo_agent.ctl import error


class CheckAgentIsLoggedStep(object):

    def execute(self, command, response, blackboard):
        if blackboard.agent_status is None:
            response.error = error.NOT_LOGGED


class CheckAgentIsNotLoggedStep(object):

    def execute(self, command, response, blackboard):
        if blackboard.agent_status is not None:
            response.error = error.ALREADY_LOGGED
