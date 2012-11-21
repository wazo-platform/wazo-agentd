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

import readline
import time
import traceback
from xivo_agent.ctl.client import AgentClient
from xivo_agent.exception import AgentError


def main():
    agent_client = AgentClient()
    try:
        agent_client.connect('localhost')
        _loop(agent_client)
    finally:
        agent_client.close()


def _loop(agent_client):
    try:
        while True:
            try:
                line = raw_input('agentctl> ').strip()
                if not line:
                    continue

                tokens = line.split()
                cmd_name, args = tokens[0], tokens[1:]
                start_time = time.time()
                if cmd_name == 'login':
                    agent_num = int(args[0])
                    extension = args[1]
                    context = args[2]
                    agent_client.login_agent(agent_num, extension, context)
                elif cmd_name == 'logoff':
                    agent_num = int(args[0])
                    agent_client.logoff_agent(agent_num)
                elif cmd_name == 'status':
                    agent_num = int(args[0])
                    status = agent_client.get_agent_status(agent_num)
                    print status
                else:
                    print 'unknown command:', cmd_name
                    continue

                print 'request took %s ms' % ((time.time() - start_time) * 1000)
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
