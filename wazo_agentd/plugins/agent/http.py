# Copyright 2024-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from typing import TYPE_CHECKING

from flask import request
from xivo.auth_verifier import required_acl
from xivo.tenant_flask_helpers import token

from wazo_agentd.http import AuthResource

from .schemas import (
    agent_login_schema,
    pause_schema,
    queue_schema,
    user_agent_login_schema,
)

if TYPE_CHECKING:
    from wazo_agentd.service.proxy import ServiceProxy


class _BaseAgentResource(AuthResource):
    service_proxy: ServiceProxy

    def __init__(self, service_proxy):
        self.service_proxy = service_proxy


class AgentById(_BaseAgentResource):
    @required_acl('agentd.agents.by-id.{agent_id}.read')
    def get(self, agent_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        return self.service_proxy.get_agent_status_by_id(
            agent_id, tenant_uuids=tenant_uuids
        )


class AgentByNumber(_BaseAgentResource):
    @required_acl('agentd.agents.by-number.{agent_number}.read')
    def get(self, agent_number):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        return self.service_proxy.get_agent_status_by_number(
            agent_number, tenant_uuids=tenant_uuids
        )


class UserAgent(_BaseAgentResource):
    @required_acl('agentd.users.me.agents.read')
    def get(self):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        user_uuid = token.user_uuid
        return self.service_proxy.get_user_agent_status(
            user_uuid, tenant_uuids=tenant_uuids
        )


class LoginAgentById(_BaseAgentResource):
    @required_acl('agentd.agents.by-id.{agent_id}.login.create')
    def post(self, agent_id):
        body = agent_login_schema.load(request.get_json(force=True))
        tenant_uuids = self._build_tenant_list({'recurse': True})
        self.service_proxy.login_agent_by_id(
            agent_id,
            body['extension'],
            body['context'],
            body['endpoint'],
            tenant_uuids=tenant_uuids,
        )
        return '', 204


class LoginAgentByNumber(_BaseAgentResource):
    @required_acl('agentd.agents.by-number.{agent_number}.login.create')
    def post(self, agent_number):
        body = agent_login_schema.load(request.get_json(force=True))
        tenant_uuids = self._build_tenant_list({'recurse': True})
        self.service_proxy.login_agent_by_number(
            agent_number,
            body['extension'],
            body['context'],
            body['endpoint'],
            tenant_uuids=tenant_uuids,
        )
        return '', 204


class LoginUserAgent(_BaseAgentResource):
    @required_acl('agentd.users.me.agents.login.create')
    def post(self):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        user_uuid = token.user_uuid
        body = user_agent_login_schema.load(request.get_json(force=True))
        self.service_proxy.login_user_agent(
            user_uuid, body['line_id'], tenant_uuids=tenant_uuids
        )
        return '', 204


class LogoffAgentById(_BaseAgentResource):
    @required_acl('agentd.agents.by-id.{agent_id}.logoff.create')
    def post(self, agent_id):
        # XXX logoff_agent_by_id raise a AgentNotLoggedError even if the agent doesn't exist;
        #     that means that logoff currently returns a 409 for an inexistant agent, not a 404
        tenant_uuids = self._build_tenant_list({'recurse': True})
        self.service_proxy.logoff_agent_by_id(agent_id, tenant_uuids=tenant_uuids)
        return '', 204


class LogoffAgentByNumber(_BaseAgentResource):
    @required_acl('agentd.agents.by-number.{agent_number}.logoff.create')
    def post(self, agent_number):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        self.service_proxy.logoff_agent_by_number(
            agent_number, tenant_uuids=tenant_uuids
        )
        return '', 204


class LogoffUserAgent(_BaseAgentResource):
    @required_acl('agentd.users.me.agents.logoff.create')
    def post(self):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        user_uuid = token.user_uuid
        self.service_proxy.logoff_user_agent(user_uuid, tenant_uuids=tenant_uuids)
        return '', 204


class AddAgentToQueue(_BaseAgentResource):
    @required_acl('agentd.agents.by-id.{agent_id}.add.create')
    def post(self, agent_id):
        body = queue_schema.load(request.get_json(force=True))
        tenant_uuids = self._build_tenant_list({'recurse': True})
        self.service_proxy.add_agent_to_queue(
            agent_id, body['queue_id'], tenant_uuids=tenant_uuids
        )
        return '', 204


class RemoveAgentFromQueue(_BaseAgentResource):
    @required_acl('agentd.agents.by-id.{agent_id}.delete.create')
    def post(self, agent_id):
        body = queue_schema.load(request.get_json(force=True))
        tenant_uuids = self._build_tenant_list({'recurse': True})
        self.service_proxy.remove_agent_from_queue(
            agent_id, body['queue_id'], tenant_uuids=tenant_uuids
        )
        return '', 204


class PauseAgentByNumber(_BaseAgentResource):
    @required_acl('agentd.agents.by-number.{agent_number}.pause.create')
    def post(self, agent_number):
        body = pause_schema.load(request.get_json(force=True))
        tenant_uuids = self._build_tenant_list({'recurse': True})
        self.service_proxy.pause_agent_by_number(
            agent_number, body['reason'], tenant_uuids=tenant_uuids
        )
        return '', 204


class PauseUserAgent(_BaseAgentResource):
    @required_acl('agentd.users.me.agents.pause.create')
    def post(self):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        body = pause_schema.load(request.get_json(force=True))
        user_uuid = token.user_uuid
        self.service_proxy.pause_user_agent(
            user_uuid, body['reason'], tenant_uuids=tenant_uuids
        )
        return '', 204


class UnpauseAgentByNumber(_BaseAgentResource):
    @required_acl('agentd.agents.by-number.{agent_number}.unpause.create')
    def post(self, agent_number):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        self.service_proxy.unpause_agent_by_number(
            agent_number, tenant_uuids=tenant_uuids
        )
        return '', 204


class UnpauseUserAgent(_BaseAgentResource):
    @required_acl('agentd.users.me.agents.unpause.create')
    def post(self):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        user_uuid = token.user_uuid
        self.service_proxy.unpause_user_agent(user_uuid, tenant_uuids=tenant_uuids)
        return '', 204


class QueueLoginUserAgent(_BaseAgentResource):
    @required_acl('agentd.users.me.agents.queues.{queue_id}.login.update')
    def put(self, queue_id: int):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        user_uuid = token.user_uuid
        self.service_proxy.login_user_agent_to_queue(user_uuid, queue_id, tenant_uuids)
        return '', 204


class QueueLogoffUserAgent(_BaseAgentResource):
    @required_acl('agentd.users.me.agents.queues.{queue_id}.logoff.update')
    def put(self, queue_id: int):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        user_uuid = token.user_uuid
        self.service_proxy.logoff_user_agent_from_queue(
            user_uuid, queue_id, tenant_uuids
        )
        return '', 204
