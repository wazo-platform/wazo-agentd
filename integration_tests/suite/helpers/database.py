# Copyright 2019-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import sqlalchemy as sa

from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from xivo_dao.alchemy.agent_membership_status import AgentMembershipStatus
from xivo_dao.alchemy.agentfeatures import AgentFeatures as Agent
from xivo_dao.alchemy.agent_login_status import AgentLoginStatus
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.line_extension import LineExtension
from xivo_dao.alchemy.linefeatures import LineFeatures as Line
from xivo_dao.alchemy.queuefeatures import QueueFeatures as Queue
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.userfeatures import UserFeatures as User
from xivo_dao.tests.test_dao import ItemInserter

logger = logging.getLogger(__name__)

# This tenant_uuid is populated into the test database
TENANT_UUID = 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeee1'


class DbHelper:
    TEMPLATE = "xivotemplate"

    @classmethod
    def build(cls, user, password, host, port, db):
        uri = f"postgresql://{user}:{password}@{host}:{port}"
        return cls(uri, db)

    def __init__(self, uri, db):
        self.uri = uri
        self.db = db
        self._engine = self.create_engine()

    def is_up(self):
        try:
            self.connect()
            return True
        except Exception as e:
            logger.debug('Database is down: %s', e)
            return False

    def create_engine(self, db=None, isolate=False):
        db = db or self.db
        uri = f"{self.uri}/{db}"
        if isolate:
            return sa.create_engine(uri, isolation_level='AUTOCOMMIT')
        return sa.create_engine(uri)

    def connect(self):
        return self._engine.connect()

    def recreate(self):
        engine = self.create_engine("postgres", isolate=True)
        connection = engine.connect()
        connection.execute(
            f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{self.db}'
            AND pid <> pg_backend_pid()
            """
        )
        connection.execute(f"DROP DATABASE IF EXISTS {self.db}")
        connection.execute(f"CREATE DATABASE {self.db} TEMPLATE {self.TEMPLATE}")
        connection.close()

    def execute(self, query, **kwargs):
        with self.connect() as connection:
            connection.execute(text(query), **kwargs)

    @contextmanager
    def queries(self):
        with self.connect() as connection:
            yield DatabaseQueries(connection)


class DatabaseQueries:
    def __init__(self, connection):
        self.connection = connection
        self.Session = sessionmaker(bind=connection)

    @contextmanager
    def inserter(self):
        session = self.Session()
        yield ItemInserter(session, tenant_uuid=TENANT_UUID)
        session.commit()

    def insert_agent(self, **kwargs):
        with self.inserter() as inserter:
            return inserter.add_agent(**kwargs).id

    def delete_agent(self, agent_id):
        session = self.Session()
        session.query(Agent).filter(Agent.id == agent_id).delete()
        session.query(AgentLoginStatus).filter(
            AgentLoginStatus.agent_id == agent_id
        ).delete()
        session.commit()

    def insert_queue(self, **kwargs):
        with self.inserter() as inserter:
            return inserter.add_queuefeatures(**kwargs).id

    def delete_queue(self, queue_id):
        session = self.Session()
        session.query(Queue).filter(Queue.id == queue_id).delete()
        session.commit()

    def associate_user_agent(self, user_id, agent_id):
        session = self.Session()
        user = session.query(User).get(user_id)
        user.agent_id = agent_id
        session.commit()

    def dissociate_user_agent(self, user_id, agent_id):
        del agent_id
        session = self.Session()
        user = session.query(User).get(user_id)
        user.agent_id = None
        session.commit()

    def associate_queue_agent(self, queue_id, agent_id):
        with self.inserter() as inserter:
            queue = inserter.session.query(Queue).get(queue_id)
            agent = inserter.session.query(Agent).get(agent_id)
            return inserter.add_queue_member(
                queue_name=queue.name,
                interface=f'PJSIP/{agent.users[0].lines[0].endpoint_sip.name}',
                usertype='agent',
                category='queue',
                channel='Agent',
                userid=agent.id,
            )

    def insert_agent_membership_status(self, queue_id, agent_id):
        session = self.Session()
        queue = session.query(Queue).get(queue_id)
        agent_membership_status = AgentMembershipStatus(
            queue_id=queue_id, agent_id=agent_id, queue_name=queue.name
        )
        session.add(agent_membership_status)
        session.commit()

    def get_agent_membership_status(self, queue_id, agent_id):
        session = self.Session()
        return (
            session.query(AgentMembershipStatus)
            .filter(
                AgentMembershipStatus.agent_id == agent_id,
                AgentMembershipStatus.queue_id == queue_id,
            )
            .first()
        )

    def insert_user_line_extension(self, **kwargs):
        with self.inserter() as inserter:
            sip = inserter.add_endpoint_sip()
            kwargs['endpoint_sip_uuid'] = sip.uuid
            user_line = inserter.add_user_line_with_exten(**kwargs)
            return {
                'user_id': user_line.user.id,
                'user_uuid': user_line.user.uuid,
                'line_id': user_line.line.id,
                'extension_id': user_line.line.extensions[0].id,
                'device_name': user_line.line.name,
            }

    def delete_user_line_extension(self, user_id, line_id, extension_id):
        session = self.Session()
        session.query(LineExtension).filter(
            LineExtension.line_id == line_id, LineExtension.extension_id == extension_id
        ).delete()
        session.query(Extension).filter(Extension.id == extension_id).delete()
        session.query(UserLine).filter(
            UserLine.user_id == user_id, UserLine.line_id == line_id
        ).delete()
        session.query(Line).filter(Line.id == line_id).delete()
        session.query(User).filter(User.id == user_id).delete()
        session.commit()
