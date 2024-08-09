# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo.auth_verifier import required_acl

from wazo_agentd.http import AuthResource


class _BaseAgentResource(AuthResource):
    def __init__(self, service_proxy):
        self.service_proxy = service_proxy


class Agents(_BaseAgentResource):
    @required_acl('agentd.agents.read')
    def get(self):
        params = self.parse_params()
        tenant_uuids = self._build_tenant_list(params)
        return self.service_proxy.get_agent_statuses(tenant_uuids=tenant_uuids)


class LogoffAgents(_BaseAgentResource):
    @required_acl('agentd.agents.logoff.create')
    def post(self):
        params = self.parse_params()
        tenant_uuids = self._build_tenant_list(params)
        self.service_proxy.logoff_all(tenant_uuids=tenant_uuids)
        return '', 204


class RelogAgents(_BaseAgentResource):
    @required_acl('agentd.agents.relog.create')
    def post(self):
        params = self.parse_params()
        tenant_uuids = self._build_tenant_list(params)
        self.service_proxy.relog_all(tenant_uuids=tenant_uuids)
        return '', 204
