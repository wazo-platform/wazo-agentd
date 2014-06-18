# -*- coding: utf-8 -*-

# Copyright (C) 2012-2014 Avencall
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
from contextlib import contextmanager
from xivo import daemonize
from xivo.xivo_logging import setup_logging
from xivo_agent import ami
from xivo_agent.ctl.server import AgentServer
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
from xivo_dao import agent_dao as orig_agent_dao
from xivo_dao import agent_status_dao
from xivo_dao import line_dao
from xivo_dao import queue_dao as orig_queue_dao
from xivo_dao import queue_log_dao
from xivo_dao import queue_member_dao

_LOG_FILENAME = '/var/log/xivo-agentd.log'
_PID_FILENAME = '/var/run/xivo-agentd.pid'

logger = logging.getLogger(__name__)


def main():
    parsed_args = _parse_args()

    setup_logging(_LOG_FILENAME, parsed_args.foreground, parsed_args.verbose)

    if not parsed_args.foreground:
        daemonize.daemonize()

    logger.info('Starting xivo-agentd')
    daemonize.lock_pidfile_or_die(_PID_FILENAME)
    try:
        _run()
    except Exception:
        logger.exception('Unexpected error:')
    finally:
        logger.info('Stopping xivo-agentd')
        daemonize.unlock_pidfile(_PID_FILENAME)


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--foreground', action='store_true',
                        help='run in foreground')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='increase verbosity')
    return parser.parse_args()


def _run():
    _init_signal()
    agent_dao = AgentDAOAdapter(orig_agent_dao)
    queue_dao = QueueDAOAdapter(orig_queue_dao)
    with _new_ami_client() as ami_client:
        with _new_agent_server() as agent_server:
            queue_log_manager = QueueLogManager(queue_log_dao)

            add_to_queue_action = AddToQueueAction(ami_client, agent_status_dao)
            login_action = LoginAction(ami_client, queue_log_manager, agent_status_dao, line_dao)
            logoff_action = LogoffAction(ami_client, queue_log_manager, agent_status_dao)
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

            handlers = [
                LoginHandler(login_manager, agent_dao),
                LogoffHandler(logoff_manager, agent_status_dao),
                MembershipHandler(add_member_manager, remove_member_manager, agent_dao, queue_dao),
                OnAgentHandler(on_agent_deleted_manager, on_agent_updated_manager, agent_dao),
                OnQueueHandler(on_queue_added_manager, on_queue_updated_manager, on_queue_deleted_manager, queue_dao),
                PauseHandler(pause_manager, agent_status_dao),
                RelogHandler(relog_manager),
                StatusHandler(agent_dao, agent_status_dao),
            ]

            for handler in handlers:
                handler.register_commands(agent_server)

            agent_server.run()


def _init_signal():
    signal.signal(signal.SIGTERM, _handle_sigterm)


def _handle_sigterm(signum, frame):
    raise SystemExit()


@contextmanager
def _new_ami_client():
    ami_client = ami.new_client('localhost', 'xivo_agent', 'die0Ahn8tae')
    try:
        yield ami_client
    finally:
        ami_client.close()


@contextmanager
def _new_agent_server():
    agent_server = AgentServer()
    try:
        yield agent_server
    finally:
        agent_server.close()


if __name__ == '__main__':
    main()
