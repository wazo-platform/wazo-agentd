# -*- coding: UTF-8 -*-

import argparse
import readline
import time
import traceback
from xivo_agent.ctl.client import Client
from xivo_agent.exception import AgentError


def main():
    parsed_args = _parse_args()

    ctl_client = Client()
    try:
        ctl_client.connect(parsed_args.hostname)
        _loop(ctl_client)
    finally:
        ctl_client.close()


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('hostname')
    return parser.parse_args()


def _loop(ctl_client):
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
                    agent_interface = args[1]
                    ctl_client.login_agent(agent_num, agent_interface)
                elif cmd_name == 'logoff':
                    agent_num = int(args[0])
                    ctl_client.logoff_agent(agent_num)
                elif cmd_name == 'status':
                    agent_num = int(args[0])
                    status = ctl_client.get_agent_status(agent_num)
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
