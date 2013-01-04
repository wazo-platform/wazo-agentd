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

from __future__ import print_function
from __future__ import unicode_literals

import argparse
import readline
import time
import traceback
from contextlib import contextmanager
from operator import attrgetter
from xivo_agent.ctl.client import AgentClient
from xivo_agent.exception import AgentError

verbose = False


@contextmanager
def _agent_client(host, port):
    agent_client = AgentClient()
    agent_client.connect(host, port)
    try:
        yield agent_client
    finally:
        agent_client.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--command',
                        help='run command')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='increase verbosity')
    parser.add_argument('-H', '--host', default=AgentClient.DEFAULT_HOST,
                        help='rabbitmq host')
    parser.add_argument('-p', '--port', type=int, default=AgentClient.DEFAULT_PORT,
                        help='rabbitmq port')

    parsed_args = parser.parse_args()

    if parsed_args.verbose:
        global verbose
        verbose = True

    with _agent_client(parsed_args.host, parsed_args.port) as agent_client:
        if parsed_args.command:
            _execute_command(parsed_args.command, agent_client)
        else:
            _loop(agent_client)


def _loop(agent_client):
    try:
        while True:
            try:
                line = raw_input('agentctl> ').strip()
                if not line:
                    continue

                _execute_command(line, agent_client)

            except KeyboardInterrupt:
                print()
            except EOFError:
                raise
            except AgentError as e:
                print('Agent error:', e)
            except Exception:
                print('Unexpected exception:')
                traceback.print_exc()
    except EOFError:
        print()


def _execute_command(line, agent_client):
    tokens = line.split()
    cmd_name, args = tokens[0], tokens[1:]
    start_time = time.time()
    if cmd_name == 'add_agent':
        agent_id = args[0]
        queue_id = args[1]
        agent_client.add_agent_to_queue(agent_id, queue_id)
    elif cmd_name == 'remove_agent':
        agent_id = args[0]
        queue_id = args[1]
        agent_client.remove_agent_from_queue(agent_id, queue_id)
    elif cmd_name == 'login':
        agent_number = args[0]
        extension = args[1]
        context = args[2]
        agent_client.login_agent_by_number(agent_number, extension, context)
    elif cmd_name == 'logoff':
        agent_number = args[0]
        agent_client.logoff_agent_by_number(agent_number)
    elif cmd_name == 'logoff_all':
        agent_client.logoff_all_agents()
    elif cmd_name == 'status':
        agent_number = args[0]
        agent_status = agent_client.get_agent_status_by_number(agent_number)
        _print_agent_status(agent_status)
    elif cmd_name == 'statuses':
        agent_statuses = agent_client.get_agent_statuses()
        for agent_status in sorted(agent_statuses, key=attrgetter('number')):
            _print_agent_status(agent_status)
    elif cmd_name == 'ping':
        print(agent_client.ping())
    else:
        print('unknown command:', cmd_name)

    if verbose:
        request_time = (time.time() - start_time) * 1000
        print('request took {0} ms'.format(request_time))


def _print_agent_status(agent_status):
    print('Agent/{0.number} (ID {0.id})'.format(agent_status))
    print('    logged: {0.logged}'.format(agent_status))


if __name__ == '__main__':
    main()
