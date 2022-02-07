# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import Schema, pre_load, EXCLUDE

from xivo.mallow import fields, validate


class BaseSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    @pre_load
    def ensure_dict(self, data, **kwargs):
        return data or {}


class AgentLoginSchema(BaseSchema):
    extension = fields.String(required=True)
    context = fields.String(required=True)


class UserAgentLoginSchema(BaseSchema):
    line_id = fields.Integer(required=True)


class PauseSchema(BaseSchema):
    reason = fields.String(
        validate=validate.Length(min=1, max=80), missing=None, default=None
    )


class QueueSchema(BaseSchema):
    queue_id = fields.Integer(required=True)


agent_login_schema = AgentLoginSchema()
pause_schema = PauseSchema()
queue_schema = QueueSchema()
user_agent_login_schema = UserAgentLoginSchema()
