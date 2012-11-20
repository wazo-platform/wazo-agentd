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

from collections import namedtuple
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.sql import select, and_


_engine = None
_agentfeatures = None
_queuemember = None
_Agent = namedtuple('_Agent', ['id', 'queues'])
_Queue = namedtuple('_Queue', ['name'])


def init(url):
    global _engine
    if _engine is not None:
        raise Exception('already initialized')

    _engine = create_engine(url)
    metadata = MetaData()

    global _agentfeatures
    _agentfeatures = Table('agentfeatures', metadata, autoload=True, autoload_with=_engine)

    global _queuemember
    _queuemember = Table('queuemember', metadata, autoload=True, autoload_with=_engine)


def agent_with_number(agent_number):
    agent_number = unicode(agent_number)

    conn = _engine.connect()
    try:
        agent = _get_agent_with_number(conn, agent_number)
        _add_queues_to_agent(conn, agent)
        return agent
    finally:
        conn.close()


def _get_agent_with_number(conn, agent_number):
    query = select([_agentfeatures.c.id], _agentfeatures.c.number == agent_number)
    row = conn.execute(query).first()
    if row is None:
        raise Exception('no agent with number %r' % agent_number)
    return _Agent(row['id'], [])


def _add_queues_to_agent(conn, agent):
    query = select([_queuemember.c.queue_name],
                and_(_queuemember.c.usertype == u'agent',
                     _queuemember.c.userid == agent.id))
    for row in conn.execute(query):
        queue = _Queue(row['queue_name'])
        agent.queues.append(queue)
