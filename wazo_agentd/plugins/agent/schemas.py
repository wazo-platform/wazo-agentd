# Copyright 2020-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo.mallow import fields, validate
from xivo.mallow_helpers import ListSchema, Schema


class AgentLoginSchema(Schema):
    extension = fields.String(required=True)
    context = fields.String(required=True)


class UserAgentLoginSchema(Schema):
    line_id = fields.Integer(required=True)


class PauseSchema(Schema):
    reason = fields.String(
        validate=validate.Length(min=1, max=80), load_default=None, dump_default=None
    )


class QueueSchema(Schema):
    queue_id = fields.Integer(required=True)


class QueueListSchema(ListSchema):
    default_sort_column = 'id'
    sort_columns = ['id', 'name', 'display_name']
    default_direction = 'asc'


agent_login_schema = AgentLoginSchema()
pause_schema = PauseSchema()
queue_schema = QueueSchema()
user_agent_login_schema = UserAgentLoginSchema()
queue_list_schema = QueueListSchema()
