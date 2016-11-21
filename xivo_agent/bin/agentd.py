# -*- coding: utf-8 -*-

# Copyright (C) 2012-2016 Avencall
# Copyright (C) 2016 Proformatique
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import argparse
import logging
import signal
import xivo_dao

from functools import partial
from kombu import Connection, Producer, Exchange
from contextlib import contextmanager

from xivo.chain_map import ChainMap
from xivo.config_helper import read_config_file_hierarchy, set_xivo_uuid
from xivo.consul_helpers import ServiceCatalogRegistration
from xivo.daemonize import pidfile_context
from xivo.http_helpers import DEFAULT_CIPHERS
from xivo.user_rights import change_user
from xivo.xivo_logging import setup_logging, silence_loggers

from xivo_agent import ami
from xivo_agent import amqp
from xivo_agent import http
from xivo_agent.dao import QueueDAOAdapter, AgentDAOAdapter
from xivo_agent.queuelog import QueueLogManager
from xivo_agent.service.action.add import AddToQueueAction
from xivo_agent.service.action.login import LoginAction
from xivo_agent.service.action.logoff import LogoffAction
from xivo_agent.service.action.pause import PauseAction
from xivo_agent.service.action.remove import RemoveFromQueueAction
from xivo_agent.service.action.update import UpdatePenaltyAction
from xivo_agent.service.handler.login import LoginHandler
from xivo_agent.service.handler.logoff import LogoffHandler
from xivo_agent.service.handler.membership import MembershipHandler
from xivo_agent.service.handler.on_agent import OnAgentHandler
from xivo_agent.service.handler.on_queue import OnQueueHandler
from xivo_agent.service.handler.pause import PauseHandler
from xivo_agent.service.handler.relog import RelogHandler
from xivo_agent.service.handler.status import StatusHandler
from xivo_agent.service.manager.add_member import AddMemberManager
from xivo_agent.service.manager.login import LoginManager
from xivo_agent.service.manager.logoff import LogoffManager
from xivo_agent.service.manager.on_agent_deleted import OnAgentDeletedManager
from xivo_agent.service.manager.on_agent_updated import OnAgentUpdatedManager
from xivo_agent.service.manager.on_queue_added import OnQueueAddedManager
from xivo_agent.service.manager.on_queue_deleted import OnQueueDeletedManager
from xivo_agent.service.manager.on_queue_updated import OnQueueUpdatedManager
from xivo_agent.service.manager.pause import PauseManager
from xivo_agent.service.manager.relog import RelogManager
from xivo_agent.service.manager.remove_member import RemoveMemberManager
from xivo_agent.service.proxy import ServiceProxy
from xivo_agent.service_discovery import self_check
from xivo_auth_client import Client as AuthClient
from xivo_bus import Marshaler, Publisher
from xivo_dao import agent_dao as orig_agent_dao
from xivo_dao import agent_status_dao
from xivo_dao import line_dao
from xivo_dao import queue_dao as orig_queue_dao
from xivo_dao import queue_log_dao
from xivo_dao import queue_member_dao

_DEFAULT_HTTPS_PORT = 9493
_DEFAULT_CONFIG = {
    'user': 'xivo-agentd',
    'auth': {
        'host': 'localhost',
        'port': 9497,
        'verify_certificate': '/usr/share/xivo-certs/server.crt',
    },
    'debug': False,
    'foreground': False,
    'logfile': '/var/log/xivo-agentd.log',
    'pidfile': '/var/run/xivo-agentd/xivo-agentd.pid',
    'config_file': '/etc/xivo-agentd/config.yml',
    'extra_config_files': '/etc/xivo-agentd/conf.d/',
    'ami': {
        'host': 'localhost',
        'username': 'xivo_agent',
        'password': 'die0Ahn8tae',
    },
    'rest_api': {
        'https': {
            'listen': '127.0.0.1',
            'port': _DEFAULT_HTTPS_PORT,
            'certificate': '/usr/share/xivo-certs/server.crt',
            'private_key': '/usr/share/xivo-certs/server.key',
            'ciphers': DEFAULT_CIPHERS,
        },
        'cors': {
            'enabled': True,
            'allow_headers': 'Content-Type',
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
    config = ChainMap(cli_config, file_config, _DEFAULT_CONFIG)

    user = config.get('user')
    if user:
        change_user(user)

    xivo_dao.init_db_from_config(config)

    setup_logging(config['logfile'], config['foreground'], config['debug'])
    silence_loggers(['Flask-Cors'], logging.WARNING)
    set_xivo_uuid(config, logger)

    with pidfile_context(config['pidfile'], config['foreground']):
        logger.info('Starting xivo-agentd')
        try:
            _run(config)
        except Exception:
            logger.exception('Unexpected error:')
        except KeyboardInterrupt:
            pass
        finally:
            logger.info('Stopping xivo-agentd')


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


def _run(config):
    _init_signal()
    xivo_uuid = config['uuid']
    agent_dao = AgentDAOAdapter(orig_agent_dao)
    queue_dao = QueueDAOAdapter(orig_queue_dao)
    auth_client = AuthClient(**config['auth'])
    with _new_ami_client(config) as ami_client:
        with _new_bus_connection(config) as producer_conn, _new_bus_connection(config) as consumer_conn:
            bus_exchange = Exchange(config['bus']['exchange_name'],
                                    type=config['bus']['exchange_type'])
            bus_producer = Producer(producer_conn, exchange=bus_exchange, auto_declare=True)
            bus_marshaler = Marshaler(xivo_uuid)
            bus_publisher = Publisher(bus_producer, bus_marshaler)

            queue_log_manager = QueueLogManager(queue_log_dao)

            add_to_queue_action = AddToQueueAction(ami_client, agent_status_dao)
            login_action = LoginAction(ami_client, queue_log_manager, agent_status_dao, line_dao, bus_publisher)
            logoff_action = LogoffAction(ami_client, queue_log_manager, agent_status_dao, bus_publisher)
            pause_action = PauseAction(ami_client)
            remove_from_queue_action = RemoveFromQueueAction(ami_client, agent_status_dao)
            update_penalty_action = UpdatePenaltyAction(ami_client, agent_status_dao)

            add_member_manager = AddMemberManager(add_to_queue_action, ami_client, agent_status_dao, queue_member_dao)
            login_manager = LoginManager(login_action, agent_status_dao)
            logoff_manager = LogoffManager(logoff_action, agent_status_dao)
            on_agent_deleted_manager = OnAgentDeletedManager(logoff_manager, agent_status_dao)
            on_agent_updated_manager = OnAgentUpdatedManager(add_to_queue_action, remove_from_queue_action, update_penalty_action, agent_status_dao)
            on_queue_added_manager = OnQueueAddedManager(add_to_queue_action, agent_status_dao)
            on_queue_deleted_manager = OnQueueDeletedManager(agent_status_dao)
            on_queue_updated_manager = OnQueueUpdatedManager(add_to_queue_action, remove_from_queue_action, agent_status_dao)
            pause_manager = PauseManager(pause_action)
            relog_manager = RelogManager(login_action, logoff_action, agent_dao, agent_status_dao)
            remove_member_manager = RemoveMemberManager(remove_from_queue_action, ami_client, agent_status_dao, queue_member_dao)

            service_proxy = ServiceProxy()
            service_proxy.login_handler = LoginHandler(login_manager, agent_dao)
            service_proxy.logoff_handler = LogoffHandler(logoff_manager, agent_status_dao)
            service_proxy.membership_handler = MembershipHandler(add_member_manager, remove_member_manager, agent_dao, queue_dao)
            service_proxy.on_agent_handler = OnAgentHandler(on_agent_deleted_manager, on_agent_updated_manager, agent_dao)
            service_proxy.on_queue_handler = OnQueueHandler(on_queue_added_manager, on_queue_updated_manager, on_queue_deleted_manager, queue_dao)
            service_proxy.pause_handler = PauseHandler(pause_manager, agent_status_dao)
            service_proxy.relog_handler = RelogHandler(relog_manager)
            service_proxy.status_handler = StatusHandler(agent_dao, agent_status_dao, xivo_uuid)

            amqp_iface = amqp.AMQPInterface(consumer_conn, bus_exchange, service_proxy)
            http_iface = http.HTTPInterface(config['rest_api'], service_proxy, auth_client)

            amqp_iface.start()
            try:
                with ServiceCatalogRegistration('xivo-agentd',
                                                xivo_uuid,
                                                config['consul'],
                                                config['service_discovery'],
                                                config['bus'],
                                                partial(self_check,
                                                        config['rest_api']['https']['port'],
                                                        config['rest_api']['https']['certificate'])):
                    http_iface.run()
            finally:
                amqp_iface.stop()


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


def _new_bus_connection(config):
    url = 'amqp://{username}:{password}@{host}:{port}//'.format(**config['bus'])
    return Connection(url)


if __name__ == '__main__':
    main()
