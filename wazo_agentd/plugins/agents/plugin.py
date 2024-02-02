# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


from .http import _Agents, _LogoffAgents, _RelogAgents


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        service_proxy = dependencies['service_proxy']

        api.add_resource(
            _Agents,
            '/agents',
            resource_class_args=[service_proxy],
        )

        api.add_resource(
            _LogoffAgents,
            '/agents/logoff',
            resource_class_args=[service_proxy],
        )

        api.add_resource(
            _RelogAgents,
            '/agents/relog',
            resource_class_args=[service_proxy],
        )
