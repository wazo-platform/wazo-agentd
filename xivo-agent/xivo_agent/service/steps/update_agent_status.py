# -*- coding: UTF-8 -*-

from xivo_agent.ctl import commands


class UpdateAgentStatusStep(object):

    def __init__(self, agent_login_dao):
        self._agent_login_dao = agent_login_dao

    def execute(self, command, response, blackboard):
        if command.name == commands.LoginCommand.name:
            self._agent_login_dao.log_in_agent(blackboard.agent.id, blackboard.extension, blackboard.context, blackboard.interface)
        elif command.name == commands.LogoffCommand.name:
            self._agent_login_dao.log_off_agent(blackboard.agent.id)
