# Copyright 2012-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import signal
import sys

from functools import partial

import xivo_dao

from wazo_amid_client import Client as AmidClient
from wazo_auth_client import Client as AuthClient

from xivo.config_helper import set_xivo_uuid
from xivo.consul_helpers import ServiceCatalogRegistration
from xivo.token_renewer import TokenRenewer
from xivo.user_rights import change_user
from xivo.xivo_logging import setup_logging, silence_loggers

from xivo_bus.publisher import BusPublisherWithQueue
from xivo_bus.consumer import BusConsumer
from xivo_bus.resources.agent.event import EditAgentEvent, DeleteAgentEvent
from xivo_bus.resources.queue.event import EditQueueEvent, DeleteQueueEvent
from xivo_dao import agent_dao as orig_agent_dao
from xivo_dao import agent_status_dao
from xivo_dao import asterisk_conf_dao
from xivo_dao import context_dao
from xivo_dao import line_dao
from xivo_dao import queue_dao as orig_queue_dao
from xivo_dao import queue_log_dao
from xivo_dao import queue_member_dao
from xivo_dao.resources.user import dao as user_dao

from wazo_agentd import http
from wazo_agentd.bus import AgentPauseEvent
from wazo_agentd.config import load as load_config
from wazo_agentd.dao import QueueDAOAdapter, AgentDAOAdapter, ExtenFeaturesDAOAdapter
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
from wazo_agentd.service.manager.blf import BLFManager
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

logger = logging.getLogger(__name__)


def main(argv=None):
    argv = argv or sys.argv[1:]
    config = load_config(logger, argv)

    user = config.get('user')
    if user:
        change_user(user)

    xivo_dao.init_db_from_config(config)

    setup_logging(config['logfile'], debug=config['debug'])
    silence_loggers(['Flask-Cors', 'amqp'], logging.WARNING)
    set_xivo_uuid(config, logger)

    logger.info('Starting wazo-agentd')
    try:
        _run(config)
    except Exception:
        logger.exception('Unexpected error:')
    except KeyboardInterrupt:
        pass
    finally:
        logger.info('Stopping wazo-agentd')


def _run(config):
    _init_signal()
    xivo_uuid = config['uuid']
    agent_dao = AgentDAOAdapter(orig_agent_dao)
    queue_dao = QueueDAOAdapter(orig_queue_dao)
    exten_features_dao = ExtenFeaturesDAOAdapter(asterisk_conf_dao)
    amid_client = AmidClient(**config['amid'])
    auth_client = AuthClient(**config['auth'])
    token_renewer = TokenRenewer(auth_client)
    token_renewer.subscribe_to_token_change(amid_client.set_token)
    token_renewer.subscribe_to_token_change(auth_client.set_token)

    bus_consumer = BusConsumer(**config['bus'])
    bus_publisher = BusPublisherWithQueue(**config['bus'], service_uuid=xivo_uuid)

    blf_manager = BLFManager(amid_client, exten_features_dao)
    queue_log_manager = QueueLogManager(queue_log_dao)

    add_to_queue_action = AddToQueueAction(amid_client, agent_status_dao)
    login_action = LoginAction(
        amid_client,
        queue_log_manager,
        blf_manager,
        agent_status_dao,
        line_dao,
        user_dao,
        agent_dao,
        bus_publisher,
    )
    logoff_action = LogoffAction(
        amid_client,
        queue_log_manager,
        blf_manager,
        agent_status_dao,
        user_dao,
        agent_dao,
        bus_publisher,
    )
    pause_action = PauseAction(amid_client)
    remove_from_queue_action = RemoveFromQueueAction(amid_client, agent_status_dao)
    update_penalty_action = UpdatePenaltyAction(amid_client, agent_status_dao)

    add_member_manager = AddMemberManager(
        add_to_queue_action, amid_client, agent_status_dao, queue_member_dao
    )
    login_manager = LoginManager(login_action, agent_status_dao, context_dao, line_dao)
    logoff_manager = LogoffManager(logoff_action, agent_dao, agent_status_dao)
    on_agent_deleted_manager = OnAgentDeletedManager(logoff_manager, agent_status_dao)
    on_agent_updated_manager = OnAgentUpdatedManager(
        add_to_queue_action,
        remove_from_queue_action,
        update_penalty_action,
        agent_status_dao,
    )
    on_queue_added_manager = OnQueueAddedManager(add_to_queue_action, agent_status_dao)
    on_queue_deleted_manager = OnQueueDeletedManager(agent_status_dao)
    on_queue_updated_manager = OnQueueUpdatedManager(
        add_to_queue_action, remove_from_queue_action, agent_status_dao
    )
    on_queue_agent_paused_manager = OnQueueAgentPausedManager(
        agent_status_dao, user_dao, agent_dao, bus_publisher
    )
    pause_manager = PauseManager(pause_action, agent_dao)
    relog_manager = RelogManager(
        login_action, logoff_action, agent_dao, agent_status_dao
    )
    remove_member_manager = RemoveMemberManager(
        remove_from_queue_action, amid_client, agent_status_dao, queue_member_dao
    )

    service_proxy = ServiceProxy()
    service_proxy.login_handler = LoginHandler(login_manager, agent_dao)
    service_proxy.logoff_handler = LogoffHandler(logoff_manager, agent_status_dao)
    service_proxy.membership_handler = MembershipHandler(
        add_member_manager, remove_member_manager, agent_dao, queue_dao
    )
    service_proxy.on_agent_handler = OnAgentHandler(
        on_agent_deleted_manager, on_agent_updated_manager, agent_dao
    )
    service_proxy.on_queue_handler = OnQueueHandler(
        on_queue_added_manager,
        on_queue_updated_manager,
        on_queue_deleted_manager,
        on_queue_agent_paused_manager,
        queue_dao,
        agent_dao,
    )
    service_proxy.pause_handler = PauseHandler(pause_manager, agent_status_dao)
    service_proxy.relog_handler = RelogHandler(relog_manager)
    service_proxy.status_handler = StatusHandler(agent_dao, agent_status_dao, xivo_uuid)

    _init_bus_consume(bus_consumer, service_proxy)

    http_iface = http.HTTPInterface(config, service_proxy, auth_client)

    service_discovery_args = [
        'wazo-agentd',
        xivo_uuid,
        config['consul'],
        config['service_discovery'],
        config['bus'],
        partial(self_check, config['rest_api']),
    ]
    try:
        with token_renewer:
            with bus_consumer, bus_publisher:
                with ServiceCatalogRegistration(*service_discovery_args):
                    http_iface.run()
    finally:
        logger.info('wazo-agentd stopping...')


def _init_bus_consume(bus_consumer, service_proxy):
    events = (
        (EditAgentEvent.name, service_proxy.on_agent_updated),
        (DeleteAgentEvent.name, service_proxy.on_agent_deleted),
        (EditQueueEvent.name, service_proxy.on_queue_updated),
        (DeleteQueueEvent.name, service_proxy.on_queue_deleted),
        (AgentPauseEvent.name, service_proxy.on_agent_paused),
    )
    for event, action in events:
        bus_consumer.subscribe(event, action)


def _init_signal():
    signal.signal(signal.SIGTERM, _handle_sigterm)


def _handle_sigterm(signum, frame):
    raise SystemExit()
