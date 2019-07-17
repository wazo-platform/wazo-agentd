# Copyright 2012-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
import logging
import signal

from functools import partial
from contextlib import contextmanager

import xivo_dao

from wazo_auth_client import Client as AuthClient

from xivo.chain_map import ChainMap
from xivo.config_helper import read_config_file_hierarchy, set_xivo_uuid, parse_config_file
from xivo.consul_helpers import ServiceCatalogRegistration
from xivo.daemonize import pidfile_context
from xivo.token_renewer import TokenRenewer
from xivo.user_rights import change_user
from xivo.xivo_logging import setup_logging, silence_loggers

from xivo_bus.resources.agent.event import EditAgentEvent, DeleteAgentEvent
from xivo_bus.resources.queue.event import EditQueueEvent, DeleteQueueEvent
from xivo_dao import agent_dao as orig_agent_dao
from xivo_dao import agent_status_dao
from xivo_dao import context_dao
from xivo_dao import line_dao
from xivo_dao import queue_dao as orig_queue_dao
from xivo_dao import queue_log_dao
from xivo_dao import queue_member_dao
from xivo_dao.resources.user import dao as user_dao

from wazo_agentd import ami
from wazo_agentd import bus
from wazo_agentd import http
from wazo_agentd.bus import AgentPauseEvent
from wazo_agentd.dao import QueueDAOAdapter, AgentDAOAdapter
from wazo_agentd.queuelog import QueueLogManager
from wazo_agentd.service.action.add import AddToQueueAction
from wazo_agentd.service.action.login import LoginAction
from wazo_agentd.service.action.logoff import LogoffAction
from wazo_agentd.service.action.pause import PauseAction
from wazo_agentd.service.action.remove import RemoveFromQueueAction
from wazo_agentd.service.action.update import UpdatePenaltyAction
from wazo_agentd.service.handler.login import LoginHandler
from wazo_agentd.service.handler.logoff import LogoffHandler
from wazo_agentd.service.handler.membership import MembershipHandler
from wazo_agentd.service.handler.on_agent import OnAgentHandler
from wazo_agentd.service.handler.on_queue import OnQueueHandler
from wazo_agentd.service.handler.pause import PauseHandler
from wazo_agentd.service.handler.relog import RelogHandler
from wazo_agentd.service.handler.status import StatusHandler
from wazo_agentd.service.manager.add_member import AddMemberManager
from wazo_agentd.service.manager.login import LoginManager
from wazo_agentd.service.manager.logoff import LogoffManager
from wazo_agentd.service.manager.on_agent_deleted import OnAgentDeletedManager
from wazo_agentd.service.manager.on_agent_updated import OnAgentUpdatedManager
from wazo_agentd.service.manager.on_queue_added import OnQueueAddedManager
from wazo_agentd.service.manager.on_queue_deleted import OnQueueDeletedManager
from wazo_agentd.service.manager.on_queue_updated import OnQueueUpdatedManager
from wazo_agentd.service.manager.on_queue_agent_paused import OnQueueAgentPausedManager
from wazo_agentd.service.manager.pause import PauseManager
from wazo_agentd.service.manager.relog import RelogManager
from wazo_agentd.service.manager.remove_member import RemoveMemberManager
from wazo_agentd.service.proxy import ServiceProxy
from wazo_agentd.service_discovery import self_check

_DEFAULT_HTTPS_PORT = 9493
_DEFAULT_CONFIG = {
    'user': 'wazo-agentd',
    'debug': False,
    'foreground': False,
    'logfile': '/var/log/wazo-agentd.log',
    'pidfile': '/var/run/wazo-agentd/wazo-agentd.pid',
    'config_file': '/etc/wazo-agentd/config.yml',
    'extra_config_files': '/etc/wazo-agentd/conf.d/',
    'ami': {
        'host': 'localhost',
        'username': 'wazo_agentd',
        'password': 'die0Ahn8tae',
    },
    'auth': {
        'host': 'localhost',
        'port': 9497,
        'verify_certificate': '/usr/share/xivo-certs/server.crt',
        'key_file': '/var/lib/wazo-auth-keys/wazo-agentd-key.yml',
    },
    'bus': {
      'username': 'guest',
      'password': 'guest',
      'host': 'localhost',
      'port': 5672,
      'exchange_name': 'xivo',
      'exchange_type': 'topic',
    },
    'consul': {
        'scheme': 'https',
        'host': 'localhost',
        'port': 8500,
        'verify': '/usr/share/xivo-certs/server.crt',
    },
    'rest_api': {
        'https': {
            'listen': '127.0.0.1',
            'port': _DEFAULT_HTTPS_PORT,
            'certificate': '/usr/share/xivo-certs/server.crt',
            'private_key': '/usr/share/xivo-certs/server.key',
        },
        'cors': {
            'enabled': True,
            'allow_headers': ['Content-Type', 'X-Auth-Token', 'Wazo-Tenant'],
        }
    },
    'service_discovery': {
        'enabled': True,
        'advertise_address': 'localhost',
        'advertise_port': _DEFAULT_HTTPS_PORT,
        'advertise_address_interface': 'eth0',
        'refresh_interval': 25,
        'retry_interval': 2,
        'ttl_interval': 30,
        'extra_tags': [],
    },
}

logger = logging.getLogger(__name__)


def main():
    cli_config = _parse_args()
    file_config = read_config_file_hierarchy(ChainMap(cli_config, _DEFAULT_CONFIG))
    service_key = _load_key_file(ChainMap(cli_config, file_config, _DEFAULT_CONFIG))
    config = ChainMap(cli_config, service_key, file_config, _DEFAULT_CONFIG)

    user = config.get('user')
    if user:
        change_user(user)

    xivo_dao.init_db_from_config(config)

    setup_logging(config['logfile'], config['foreground'], config['debug'])
    silence_loggers(['Flask-Cors'], logging.WARNING)
    set_xivo_uuid(config, logger)

    with pidfile_context(config['pidfile'], config['foreground']):
        logger.info('Starting wazo-agentd')
        try:
            _run(config)
        except Exception:
            logger.exception('Unexpected error:')
        except KeyboardInterrupt:
            pass
        finally:
            logger.info('Stopping wazo-agentd')


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--foreground', action='store_true',
                        help='run in foreground')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='increase verbosity')
    parser.add_argument('-u', '--user', action='store', help='User to run the daemon')

    parsed = parser.parse_args()

    config = {}
    if parsed.foreground:
        config['foreground'] = parsed.foreground
    if parsed.verbose:
        config['debug'] = parsed.verbose
    if parsed.user:
        config['user'] = parsed.user

    return config


def _load_key_file(config):
    key_file = parse_config_file(config['auth']['key_file'])
    return {'auth': {'username': key_file.get('service_id'),
                     'password': key_file.get('service_key')}}


def _run(config):
    _init_signal()
    xivo_uuid = config['uuid']
    agent_dao = AgentDAOAdapter(orig_agent_dao)
    queue_dao = QueueDAOAdapter(orig_queue_dao)
    auth_client = AuthClient(**config['auth'])
    token_renewer = TokenRenewer(auth_client)
    token_renewer.subscribe_to_token_change(auth_client.set_token)

    with _new_ami_client(config) as ami_client:
        bus_consumer = bus.Consumer(config)
        bus_publisher = bus.Publisher(config)

        queue_log_manager = QueueLogManager(queue_log_dao)

        add_to_queue_action = AddToQueueAction(ami_client, agent_status_dao)
        login_action = LoginAction(ami_client, queue_log_manager, agent_status_dao, line_dao, user_dao, bus_publisher)
        logoff_action = LogoffAction(ami_client, queue_log_manager, agent_status_dao, user_dao, bus_publisher)
        pause_action = PauseAction(ami_client)
        remove_from_queue_action = RemoveFromQueueAction(ami_client, agent_status_dao)
        update_penalty_action = UpdatePenaltyAction(ami_client, agent_status_dao)

        add_member_manager = AddMemberManager(add_to_queue_action, ami_client, agent_status_dao, queue_member_dao)
        login_manager = LoginManager(login_action, agent_status_dao, context_dao)
        logoff_manager = LogoffManager(logoff_action, agent_status_dao)
        on_agent_deleted_manager = OnAgentDeletedManager(logoff_manager, agent_status_dao)
        on_agent_updated_manager = OnAgentUpdatedManager(add_to_queue_action, remove_from_queue_action, update_penalty_action, agent_status_dao)
        on_queue_added_manager = OnQueueAddedManager(add_to_queue_action, agent_status_dao)
        on_queue_deleted_manager = OnQueueDeletedManager(agent_status_dao)
        on_queue_updated_manager = OnQueueUpdatedManager(add_to_queue_action, remove_from_queue_action, agent_status_dao)
        on_queue_agent_paused_manager = OnQueueAgentPausedManager(agent_status_dao, user_dao, bus_publisher)
        pause_manager = PauseManager(pause_action)
        relog_manager = RelogManager(login_action, logoff_action, agent_dao, agent_status_dao)
        remove_member_manager = RemoveMemberManager(remove_from_queue_action, ami_client, agent_status_dao, queue_member_dao)

        service_proxy = ServiceProxy()
        service_proxy.login_handler = LoginHandler(login_manager, agent_dao)
        service_proxy.logoff_handler = LogoffHandler(logoff_manager, agent_status_dao)
        service_proxy.membership_handler = MembershipHandler(add_member_manager, remove_member_manager, agent_dao, queue_dao)
        service_proxy.on_agent_handler = OnAgentHandler(on_agent_deleted_manager, on_agent_updated_manager, agent_dao)
        service_proxy.on_queue_handler = OnQueueHandler(on_queue_added_manager, on_queue_updated_manager, on_queue_deleted_manager, on_queue_agent_paused_manager, queue_dao, agent_dao)
        service_proxy.pause_handler = PauseHandler(pause_manager, agent_status_dao)
        service_proxy.relog_handler = RelogHandler(relog_manager)
        service_proxy.status_handler = StatusHandler(agent_dao, agent_status_dao, xivo_uuid)

        bus_consumer.on_event(EditAgentEvent.name, service_proxy.on_agent_updated)
        bus_consumer.on_event(DeleteAgentEvent.name, service_proxy.on_agent_deleted)
        bus_consumer.on_event(EditQueueEvent.name, service_proxy.on_queue_updated)
        bus_consumer.on_event(DeleteQueueEvent.name, service_proxy.on_queue_deleted)
        bus_consumer.on_event(AgentPauseEvent.name, service_proxy.on_agent_paused)

        http_iface = http.HTTPInterface(config, service_proxy, auth_client)

        service_discovery_args = [
            'wazo-agentd',
            xivo_uuid,
            config['consul'],
            config['service_discovery'],
            config['bus'],
            partial(self_check, config['rest_api']['https']['port'])
        ]
        with token_renewer:
            with bus.consumer_thread(bus_consumer):
                with ServiceCatalogRegistration(*service_discovery_args):
                    http_iface.run()


def _init_signal():
    signal.signal(signal.SIGTERM, _handle_sigterm)


def _handle_sigterm(signum, frame):
    raise SystemExit()


@contextmanager
def _new_ami_client(config):
    ami_client = ami.new_client(config['ami']['host'],
                                config['ami']['username'],
                                config['ami']['password'])
    try:
        yield ami_client
    finally:
        ami_client.close()


if __name__ == '__main__':
    main()
