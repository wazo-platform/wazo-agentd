# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_test_helpers import until
from hamcrest import (
    assert_that,
    calling,
    has_entries,
    has_entry,
    has_properties,
    starts_with,
)
from wazo_agentd_client.error import AgentdClientError
from wazo_test_helpers.hamcrest.raises import raises

from .helpers.base import BaseIntegrationTest


class TestAgentdStatus(BaseIntegrationTest):

    asset = 'base'

    def setUp(self):
        super().setUp()
        self.bus = self.make_bus()
        until.true(self.bus.is_up, timeout=10)

    def test_agentd_status_is_ok(self):
        def check_all_ok():
            result = self.agentd.status()
            assert_that(
                result,
                has_entries(
                    bus_consumer=has_entry('status', 'ok'),
                    bus_publisher=has_entry('status', 'ok'),
                    service_token=has_entry('status', 'ok'),
                ),
            )

        until.assert_(check_all_ok, tries=10)


class TestAgentdRabbitMQStops(BaseIntegrationTest):

    asset = 'base'

    def setUp(self):
        super().setUp()
        self.bus = self.make_bus()
        until.true(self.bus.is_up, timeout=10)

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


class TestAgentdAuthClientStops(BaseIntegrationTest):

    asset = 'base'

    def setUp(self):
        super().setUp()
        self.bus = self.make_bus()
        until.true(self.bus.is_up, timeout=10)

    def test_given_wazo_auth_client_stops_when_status_then_status_fail(self):
        self.stop_service('agentd')
        self.stop_service('auth')
        self.start_service('agentd')
        agentd = self.make_agentd()

        def _raises_503():
            assert_that(
                calling(agentd.status),
                raises(AgentdClientError).matching(
                    has_properties(
                        error=starts_with(
                            'Could not connect to authentication server on auth'
                        ),
                    )
                ),
            )

        until.assert_(_raises_503, tries=10)
