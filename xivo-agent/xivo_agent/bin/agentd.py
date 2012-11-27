# -*- coding: UTF-8 -*-

# Copyright (C) 2012  Avencall
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
from xivo_agent import ami
from xivo_agent.ctl.server import AgentServer
from xivo_agent.queuelog import QueueLogManager
from xivo_agent.service import AgentService
from xivo_dao import queue_log_dao, agent_login_dao
from xivo_dao.alchemy import dbconnection
from xivo_dao.agentfeaturesdao import AgentFeaturesDAO

_DB_URI = 'postgresql://asterisk:proformatique@localhost/asterisk'
_LOG_FILENAME = '/var/log/xivo-agentd.log'
_PIDFILE = '/var/run/xivo-agentd.pid'


def main():
    parsed_args = _parse_args()

    _init_logging(parsed_args)

    if not parsed_args.foreground:
        daemonize.daemonize()

    daemonize.lock_pidfile_or_die(_PIDFILE)
    try:
        _run()
    finally:
        daemonize.unlock_pidfile(_PIDFILE)


def _run():
    _init_signal()
    _init_dao()
    with _new_ami_client() as ami_client:
        with _new_agent_server() as agent_server:
            queue_log_manager = QueueLogManager(queue_log_dao)
            agentfeatures_dao = AgentFeaturesDAO.new_from_uri('asterisk')

            agent_service = AgentService(ami_client, agent_server, queue_log_manager,
                                         agent_login_dao, agentfeatures_dao)
            agent_service.init()
            agent_service.run()


def _init_logging(parsed_args):
    logger = logging.getLogger()
    level = logging.DEBUG if parsed_args.verbose else logging.INFO
    logger.setLevel(level)
    if parsed_args.foreground:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s (%(levelname)s): %(message)s'))
    else:
        handler = logging.FileHandler(_LOG_FILENAME)
        handler.setFormatter(logging.Formatter('%(asctime)s [%(process)d] (%(levelname)s): %(message)s'))
    logger.addHandler(handler)


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='increase verbosity')
    parser.add_argument('-f', '--foreground', action='store_true',
                        help='run in foreground')
    return parser.parse_args()


def _init_signal():
    signal.signal(signal.SIGTERM, _handle_sigterm)


def _init_dao():
    db_connection_pool = dbconnection.DBConnectionPool(dbconnection.DBConnection)
    dbconnection.register_db_connection_pool(db_connection_pool)
    dbconnection.add_connection_as(_DB_URI, 'asterisk')


def _handle_sigterm(signum, frame):
    raise SystemExit(0)


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
        agent_server.bind('localhost')
        yield agent_server
    finally:
        agent_server.close()


if __name__ == '__main__':
    main()
