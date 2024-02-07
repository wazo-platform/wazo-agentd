# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo.auth_verifier import required_acl

from wazo_agentd.http import AuthResource


class StatusResource(AuthResource):
    def __init__(self, status_aggregator):
        self.status_aggregator = status_aggregator

    @required_acl('agentd.status.read')
    def get(self):
        return self.status_aggregator.status(), 200
