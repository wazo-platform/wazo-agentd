# -*- coding: UTF-8 -*-

from xivo_agent.ctl import error


class GetAgentStep(object):

    def __init__(self, agentfeatures_dao):
        self._agentfeatures_dao = agentfeatures_dao

    def execute(self, command, response, blackboard):
        try:
            if command.agent_id is not None:
                blackboard.agent = self._agentfeatures_dao.agent_with_id(command.agent_id)
            else:
                blackboard.agent = self._agentfeatures_dao.agent_with_number(command.agent_number)
        except LookupError:
            response.error = error.NO_SUCH_AGENT
