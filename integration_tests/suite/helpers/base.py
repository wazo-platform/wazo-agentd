# Copyright 2019-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import os
import uuid

from wazo_agentd_client import Client as AgentdClient

from xivo_test_helpers.auth import AuthClient, MockUserToken
from xivo_test_helpers.asset_launching_test_case import (
    AssetLaunchingTestCase,
    NoSuchService,
)
from .amid import AmidClient
from .bus import BusClient

from .database import DbHelper, TENANT_UUID as TOKEN_TENANT_UUID


TOKEN_UUID = '00000000-0000-0000-0000-000000000101'
TOKEN_USER_UUID = '00000000-0000-0000-0000-000000000301'

UNKNOWN_UUID = '00000000-0000-0000-0000-000000000000'
UNKNOWN_ID = 9999999999999

logger = logging.getLogger(__name__)


class BaseIntegrationTest(AssetLaunchingTestCase):

    assets_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', '..', 'assets')
    )
    service = 'agentd'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.create_token()
        cls.reset_clients()

    @classmethod
    def create_token(cls):
        cls.auth = cls.make_auth()
        if not cls.auth:
            return

        token = MockUserToken(
            TOKEN_UUID,
            TOKEN_USER_UUID,
            metadata={'uuid': TOKEN_USER_UUID, 'tenant_uuid': TOKEN_TENANT_UUID},
        )
        cls.auth.set_token(token)
        cls.auth.set_tenants(
            {
                'uuid': TOKEN_TENANT_UUID,
                'name': 'name1',
                'parent_uuid': TOKEN_TENANT_UUID,
            }
        )

    @classmethod
    def create_user_token(cls, user_uuid):
        token_uuid = str(uuid.uuid4())
        token = MockUserToken(
            token_uuid,
            user_uuid,
            metadata={'uuid': user_uuid, 'tenant_uuid': TOKEN_TENANT_UUID},
        )
        cls.auth.set_token(token)
        cls.agentd.set_token(token_uuid)
        return token_uuid

    @classmethod
    def reset_clients(cls):
        cls.amid = cls.make_amid()
        cls.agentd = cls.make_agentd()
        cls.auth = cls.make_auth()
        cls.bus = cls.make_bus()
        cls.database = cls.make_database()

        cls.amid.set_queuepause()

    @classmethod
    def make_agentd(cls, token=TOKEN_UUID):
        try:
            port = cls.service_port(9493, 'agentd')
        except NoSuchService as e:
            logger.debug(e)
            return
        return AgentdClient(
            '127.0.0.1',
            port=port,
            prefix=False,
            https=False,
            token=token,
        )

    @classmethod
    def make_auth(cls):
        try:
            port = cls.service_port(9497, 'auth')
        except NoSuchService as e:
            logger.debug(e)
            return
        return AuthClient('127.0.0.1', port=port)

    @classmethod
    def make_amid(cls):
        try:
            port = cls.service_port(9491, 'amid')
        except NoSuchService as e:
            logger.debug(e)
            return
        return AmidClient('127.0.0.1', port=port)

    @classmethod
    def make_bus(cls):
        try:
            port = cls.service_port(5672, 'rabbitmq')
        except NoSuchService as e:
            logger.debug(e)
            return
        return BusClient.from_connection_fields(host='127.0.0.1', port=port)

    @classmethod
    def make_database(cls):
        try:
            port = cls.service_port(5432, 'postgres')
        except NoSuchService as e:
            logger.debug(e)
            return
        return DbHelper.build(
            'asterisk', 'proformatique', '127.0.0.1', port, 'asterisk'
        )
