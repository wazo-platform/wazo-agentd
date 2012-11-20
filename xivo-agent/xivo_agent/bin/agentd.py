# -*- coding: UTF-8 -*-

import argparse
import logging
from xivo_agent import ami
from xivo_agent import dao
from xivo_agent.ctl.server import Server
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
        ctl_server = Server()
        try:
            ctl_server.bind('0.0.0.0')
            agent_service = AgentService(ami_client, ctl_server)
            agent_service.init()
            agent_service.run()
        finally:
            ctl_server.close()
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
