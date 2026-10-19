# Copyright 2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from unittest.mock import Mock, patch

import pytest

from wazo_agentd.http import HTTPInterface


@pytest.fixture
def http_interface():
    config = {
        'rest_api': {
            'listen': '127.0.0.1',
            'port': 9493,
            'min_threads': 1,
            'max_threads': 1,
            'certificate': None,
            'private_key': None,
            'cors': {'enabled': False},
        },
    }
    return HTTPInterface(config, Mock(), Mock(), Mock())


def test_stop_before_run_does_not_raise_and_sets_the_tombstone(http_interface):
    http_interface.stop()

    assert http_interface._stopped.is_set()


@patch('wazo_agentd.http.wsgi')
def test_run_after_stop_does_not_start_the_server(wsgi, http_interface):
    http_interface.stop()
    http_interface.run()

    wsgi.DynamicWSGIServer.return_value.start.assert_not_called()


@patch('wazo_agentd.http.wsgi')
def test_stop_after_run_stops_the_server(wsgi, http_interface):
    http_interface.run()
    http_interface.stop()

    wsgi.DynamicWSGIServer.return_value.stop.assert_called_once_with()
