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
from xivo_agent import ami
from xivo_agent import dao
from xivo_agent.ctl.server import AgentServer
from xivo_agent.service import AgentService


def main():
    _init_logging()

    parsed_args = _parse_args()

    if parsed_args.verbose:
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

    dao.init('postgresql://asterisk:proformatique@localhost/asterisk')

    ami_client = ami.new_client('localhost', 'xivo_agent', 'die0Ahn8tae')
    try:
        agent_server = AgentServer()
        try:
            agent_server.bind('0.0.0.0')
            agent_service = AgentService(ami_client, agent_server)
            agent_service.init()
            agent_service.run()
        finally:
            agent_server.close()
    finally:
        ami_client.close()


def _init_logging():
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='increase verbosity')
    return parser.parse_args()


if __name__ == '__main__':
    main()
