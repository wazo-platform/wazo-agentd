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
import readline
import time
import traceback
from xivo_agent.ctl.client import AgentClient
from xivo_agent.exception import AgentError

from contextlib import contextmanager

@contextmanager
def _agent_client():
    agent_client = AgentClient()
    agent_client.connect('localhost')
    try:
        yield agent_client
    finally:
        agent_client.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--command', help='Run command')

    opts = parser.parse_args()

    with _agent_client() as agent_client:
        if opts.command:
            _execute_command(opts.command, agent_client)
        else:
            _loop(agent_client)


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
    elif cmd_name == 'status':
        agent_number = args[0]
        print agent_client.get_agent_status_by_number(agent_number)
    elif cmd_name == 'statuses':
        print agent_client.get_agent_statuses()
    elif cmd_name == 'ping':
        print agent_client.ping()
    else:
        print 'unknown command:', cmd_name
    print 'request took %s ms' % ((time.time() - start_time) * 1000)


def _loop(agent_client):
    try:
        while True:
            try:
                line = raw_input('agentctl> ').strip()
                if not line:
                    continue

                _execute_command(line, agent_client)

            except KeyboardInterrupt:
                print
            except EOFError:
                raise
            except AgentError as e:
                print 'Agent error:', e
            except Exception:
                print 'Unexpected exception:'
                traceback.print_exc()
    except EOFError:
        print


if __name__ == '__main__':
    main()
