# Copyright 2012-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse

from xivo.chain_map import ChainMap
from xivo.config_helper import (
    read_config_file_hierarchy,
    parse_config_file,
)

_DEFAULT_HTTP_PORT = 9493
_DEFAULT_CONFIG = {
    'user': 'wazo-agentd',
    'debug': False,
    'logfile': '/var/log/wazo-agentd.log',
    'config_file': '/etc/wazo-agentd/config.yml',
    'extra_config_files': '/etc/wazo-agentd/conf.d/',
    'amid': {'host': 'localhost', 'port': 9491, 'prefix': None, 'https': False},
    'auth': {
        'host': 'localhost',
        'port': 9497,
        'prefix': None,
        'https': False,
        'key_file': '/var/lib/wazo-auth-keys/wazo-agentd-key.yml',
    },
    'bus': {
        'username': 'guest',
        'password': 'guest',
        'host': 'localhost',
        'port': 5672,
        'exchange_name': 'xivo',
        'exchange_type': 'topic',
        'subscribe': {
            'exchange_name': 'wazo-headers',
            'exchange_type': 'headers',
        },
    },
    'rest_api': {
        'listen': '127.0.0.1',
        'port': _DEFAULT_HTTP_PORT,
        'certificate': None,
        'private_key': None,
        'cors': {
            'enabled': True,
            'allow_headers': ['Content-Type', 'X-Auth-Token', 'Wazo-Tenant'],
        },
    },
    'consul': {
        'scheme': 'http',
        'port': 8500,
    },
    'service_discovery': {
        'enabled': False,
        'advertise_address': 'auto',
        'advertise_address_interface': 'eth0',
        'advertise_port': _DEFAULT_HTTP_PORT,
        'extra_tags': [],
        'refresh_interval': 27,
        'retry_interval': 2,
        'ttl_interval': 30,
    },
}


def load(logger, argv):
    cli_config = _parse_args()
    file_config = read_config_file_hierarchy(ChainMap(cli_config, _DEFAULT_CONFIG))
    service_key = _load_key_file(ChainMap(cli_config, file_config, _DEFAULT_CONFIG))
    return ChainMap(cli_config, service_key, file_config, _DEFAULT_CONFIG)


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true', help='Log debug messages')
    parser.add_argument('-u', '--user', action='store', help='User to run the daemon')

    parsed = parser.parse_args()

    config = {}
    if parsed.debug:
        config['debug'] = parsed.debug
    if parsed.user:
        config['user'] = parsed.user

    return config


def _load_key_file(config):
    if config['auth'].get('username') and config['auth'].get('password'):
        return {}

    key_file = parse_config_file(config['auth']['key_file'])
    return {
        'auth': {
            'username': key_file['service_id'],
            'password': key_file['service_key'],
        }
    }
