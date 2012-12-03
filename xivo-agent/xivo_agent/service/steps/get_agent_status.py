# -*- coding: UTF-8 -*-


class GetAgentStatusStep(object):

    def __init__(self, agent_login_dao):
        self._agent_login_dao = agent_login_dao

    def execute(self, command, response, blackboard):
        blackboard.agent_status = self._agent_login_dao.get_status(blackboard.agent.id)
