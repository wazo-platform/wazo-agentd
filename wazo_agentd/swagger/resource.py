# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import yaml

from flask import make_response
from flask_restful import Resource
from pkg_resources import resource_string
from xivo.http_helpers import reverse_proxy_fix_api_spec


class SwaggerResource(Resource):
    api_package = "wazo_agentd.swagger"
    api_filename = "api.yml"
    api_path = "/api/api.yml"

    @classmethod
    def add_resource(cls, api):
        api.add_resource(cls, cls.api_path)

    def get(self):
        try:
            api_spec = yaml.load(resource_string(self.api_package, self.api_filename))
        except OSError:
            return {'error': "API spec does not exist"}, 404
        reverse_proxy_fix_api_spec(api_spec)
        response = yaml.dump(dict(api_spec))
        return make_response(response, 200, {'Content-Type': 'application/x-yaml'})
