# Copyright 2012-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import signal
import sys
import threading
from functools import partial

import xivo_dao
from wazo_amid_client import Client as AmidClient
from wazo_auth_client import Client as AuthClient
from wazo_bus.resources.agent.event import AgentDeletedEvent, AgentEditedEvent
from wazo_bus.resources.queue.event import QueueDeletedEvent, QueueEditedEvent
from xivo import plugin_helpers
from xivo.config_helper import set_xivo_uuid
from xivo.consul_helpers import ServiceCatalogRegistration
from xivo.status import StatusAggregator, TokenStatus
from xivo.token_renewer import TokenRenewer
from xivo.user_rights import change_user
from xivo.xivo_logging import setup_logging, silence_loggers
from xivo_dao import agent_dao as orig_agent_dao
from xivo_dao import agent_status_dao, asterisk_conf_dao, context_dao, line_dao
from xivo_dao import queue_dao as orig_queue_dao
from xivo_dao import queue_log_dao, queue_member_dao
from xivo_dao.resources.user import dao as user_dao

from wazo_agentd import http
from wazo_agentd.bus import BusConsumer, BusPublisher, QueueMemberPausedEvent
from wazo_agentd.config import load as load_config
from wazo_agentd.dao import AgentDAOAdapter, ExtenFeaturesDAOAdapter, QueueDAOAdapter
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
from wazo_agentd.service.manager.agent_queues_manager import AgentQueuesManager
from wazo_agentd.service.manager.blf import BLFManager
from wazo_agentd.service.manager.login import LoginManager
from wazo_agentd.service.manager.logoff import LogoffManager
from wazo_agentd.service.manager.on_agent_deleted import OnAgentDeletedManager
from wazo_agentd.service.manager.on_agent_updated import OnAgentUpdatedManager
from wazo_agentd.service.manager.on_queue_added import OnQueueAddedManager
from wazo_agentd.service.manager.on_queue_agent_paused import OnQueueAgentPausedManager
from wazo_agentd.service.manager.on_queue_deleted import OnQueueDeletedManager
from wazo_agentd.service.manager.on_queue_updated import OnQueueUpdatedManager
from wazo_agentd.service.manager.pause import PauseManager
from wazo_agentd.service.manager.relog import RelogManager
from wazo_agentd.service.manager.remove_member import RemoveMemberManager
from wazo_agentd.service.proxy import ServiceProxy
from wazo_agentd.service_discovery import self_check

logger = logging.getLogger(__name__)

_stopping_thread = None


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

    _run(config)


def _run(config):
    xivo_uuid = config['uuid']
    agent_dao = AgentDAOAdapter(orig_agent_dao)
    queue_dao = QueueDAOAdapter(orig_queue_dao)
    exten_features_dao = ExtenFeaturesDAOAdapter(asterisk_conf_dao)
    amid_client = AmidClient(**config['amid'])
    auth_client = AuthClient(**config['auth'])
    token_renewer = TokenRenewer(auth_client)
    status_aggregator = StatusAggregator()
    token_status = TokenStatus()
    token_renewer.subscribe_to_token_change(amid_client.set_token)
    token_renewer.subscribe_to_token_change(auth_client.set_token)

    bus_consumer = BusConsumer.from_config(config['bus'])
    bus_publisher = BusPublisher.from_config(xivo_uuid, config['bus'])

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
    pause_action = PauseAction(amid_client)
    pause_manager = PauseManager(pause_action, agent_dao)
    logoff_action = LogoffAction(
        amid_client,
        queue_log_manager,
        blf_manager,
        pause_manager,
        agent_status_dao,
        user_dao,
        agent_dao,
        bus_publisher,
    )
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
    relog_manager = RelogManager(
        login_action, logoff_action, agent_dao, agent_status_dao
    )
    remove_member_manager = RemoveMemberManager(
        remove_from_queue_action, amid_client, agent_status_dao, queue_member_dao
    )
    agent_queues_manager = AgentQueuesManager(
        add_to_queue_action, remove_from_queue_action, agent_status_dao
    )

    service_proxy = ServiceProxy()
    service_proxy.login_handler = LoginHandler(login_manager, agent_dao)
    service_proxy.logoff_handler = LogoffHandler(logoff_manager, agent_status_dao)
    service_proxy.membership_handler = MembershipHandler(
        add_member_manager,
        remove_member_manager,
        agent_queues_manager,
        agent_dao,
        queue_dao,
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
    token_renewer.subscribe_to_token_change(token_status.token_change_callback)
    status_aggregator.add_provider(bus_consumer.provide_status)
    status_aggregator.add_provider(token_status.provide_status)

    http_iface = http.HTTPInterface(
        config, service_proxy, auth_client, status_aggregator
    )

    service_discovery_args = [
        'wazo-agentd',
        xivo_uuid,
        config['consul'],
        config['service_discovery'],
        config['bus'],
        partial(self_check, config['rest_api']),
    ]

    plugin_helpers.load(
        namespace='wazo_agentd.plugins',
        names=config['enabled_plugins'],
        dependencies={
            'api': http_iface.api,
            'ami': amid_client,
            'auth': auth_client,
            'bus_consumer': bus_consumer,
            'bus_publisher': bus_publisher,
            'config': config,
            'token_changed_subscribe': token_renewer.subscribe_to_token_change,
            'next_token_changed_subscribe': token_renewer.subscribe_to_next_token_change,
            'status_aggregator': status_aggregator,
            'service_proxy': service_proxy,
        },
    )

    def _handle_signal(signum, frame):
        global _stopping_thread
        reason = signal.Signals(signum).name
        logger.warning('Stopping wazo-agentd: %s', reason)
        _stopping_thread = threading.Thread(target=http_iface.stop, name=reason)
        _stopping_thread.start()

    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT, _handle_signal)

    logger.info('wazo-agentd starting...')
    try:
        with token_renewer:
            with bus_consumer:
                with ServiceCatalogRegistration(*service_discovery_args):
                    http_iface.run()
    finally:
        _stopping_thread.join()


def _init_bus_consume(bus_consumer, service_proxy):
    events = (
        (AgentEditedEvent, service_proxy.on_agent_updated),
        (AgentDeletedEvent, service_proxy.on_agent_deleted),
        (QueueEditedEvent, service_proxy.on_queue_updated),
        (QueueDeletedEvent, service_proxy.on_queue_deleted),
        (QueueMemberPausedEvent, service_proxy.on_agent_paused),
    )
    for event, action in events:
        bus_consumer.subscribe(event.name, action)
