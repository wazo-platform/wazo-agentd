# -*- coding: UTF-8 -*-


class SendAgentLoginEventStep(object):

    def __init__(self, ami_client):
        self._ami_client = ami_client

    def execute(self, command, response, blackboard):
        self._ami_client.agent_login(blackboard.agent.id, blackboard.agent.number, blackboard.extension, blackboard.context)


class SendAgentLogoffEventStep(object):

    def __init__(self, ami_client):
        self._ami_client = ami_client

    def execute(self, command, response, blackboard):
        self._ami_client.agent_logoff(blackboard.agent.id, blackboard.agent.number)
