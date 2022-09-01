# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_test_helpers import until
from hamcrest import assert_that, has_entries, has_entry

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
