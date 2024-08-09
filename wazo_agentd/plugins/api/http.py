# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

import yaml
from flask import make_response
from flask_restful import Resource
from wazo.chain_map import ChainMap
from wazo.http_helpers import reverse_proxy_fix_api_spec
from wazo.rest_api_helpers import load_all_api_specs

logger = logging.getLogger(__name__)


class SwaggerResource(Resource):
    api_filename = "api.yml"

    def get(self):
        api_spec = ChainMap(
            *load_all_api_specs('wazo_agentd.plugins', self.api_filename)
        )

        if not api_spec.get('info'):
            return {'error': "API spec does not exist"}, 404

        reverse_proxy_fix_api_spec(api_spec)
        return make_response(
            yaml.dump(dict(api_spec)), 200, {'Content-Type': 'application/x-yaml'}
        )
