# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import Schema, pre_load, EXCLUDE

from xivo.mallow import fields


class BaseSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    @pre_load
    def ensure_dict(self, data):
        return data or {}


class AgentLoginSchema(BaseSchema):
    extension = fields.String(required=True)
    context = fields.String(required=True)


class UserAgentLoginSchema(BaseSchema):
    line_id = fields.Integer(required=True)


agent_login_schema = AgentLoginSchema()
user_agent_login_schema = UserAgentLoginSchema()
