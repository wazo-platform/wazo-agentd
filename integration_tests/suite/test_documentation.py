# Copyright 2019-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import requests
import yaml

from openapi_spec_validator import validate_spec, openapi_v2_spec_validator

from .helpers.base import BaseIntegrationTest

requests.packages.urllib3.disable_warnings()

logger = logging.getLogger('openapi_spec_validator')
logger.setLevel(logging.INFO)


class TestDocumentation(BaseIntegrationTest):
    asset = 'base'

    def test_documentation_errors(self):
        port = self.service_port(9493, 'agentd')
        api_url = 'http://127.0.0.1:{port}/1.0/api/api.yml'.format(port=port)
        api = requests.get(api_url)
        validate_spec(yaml.safe_load(api.text), validator=openapi_v2_spec_validator)
