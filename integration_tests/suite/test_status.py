# Copyright 2022-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import requests
from hamcrest import assert_that, has_entries, has_entry
from wazo_test_helpers import until

from .helpers.base import BaseIntegrationTest


class TestStatus(BaseIntegrationTest):
    asset = 'base'

    def test_agentd_status_is_ok(self):
        def check_all_ok():
            result = self.agentd.status()
            assert_that(
                result,
                has_entries(
                    bus_consumer=has_entry('status', 'ok'),
                    service_token=has_entry('status', 'ok'),
                ),
            )

        until.assert_(check_all_ok, tries=10)

    def test_given_rabbitmq_stops_when_status_then_bus_status_fail(self):
        self.stop_service('rabbitmq')

        def rabbitmq_is_shut_down():
            result = self.agentd.status()

            assert_that(
                result,
                has_entries(
                    bus_consumer=has_entry('status', 'fail'),
                ),
            )

        until.assert_(rabbitmq_is_shut_down, timeout=5)

        self.start_service('rabbitmq')
        self.wait_strategy.wait(self)

    def test_given_wazo_auth_client_stops_when_status_then_status_fail(self):
        self.restart_service('auth')
        self.restart_service('agentd')
        self.reset_clients()
        until.true(self.auth.is_up, tries=10)
        self.create_token()

        def _service_token_fail():
            try:
                result = self.agentd.status()
            except requests.RequestException:
                result = {}
            assert_that(
                result,
                has_entries(
                    service_token=has_entry('status', 'fail'),
                ),
            )

        until.assert_(_service_token_fail, tries=10)

        self.create_service_token()
        self.wait_strategy.wait(self)
