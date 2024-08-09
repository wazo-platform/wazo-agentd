# Copyright 2021-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from wazo.xivo_helpers import fkey_extension
from xivo_dao.helpers import db_utils

from wazo_agentd.exception import NoSuchExtenFeatureError

logger = logging.getLogger(__name__)


class BLFManager:
    def __init__(self, amid_client, exten_features_dao):
        self._amid_client = amid_client
        self._exten_features_dao = exten_features_dao

    def set_user_blf(self, user_id, feature_name, state, target):
        with db_utils.session_scope():
            try:
                exten_prefix = self._exten_features_dao.get_extension(
                    'phoneprogfunckey'
                )
                feature_exten = self._exten_features_dao.get_extension(feature_name)
            except NoSuchExtenFeatureError:
                logger.info(
                    'cannot set BLF %s %s missing extension configuration',
                    feature_name,
                    state,
                )
                return

        hint = fkey_extension(exten_prefix, (user_id, feature_exten, target))
        cli_command = f'devstate change Custom:{hint} {state}'
        result = self._amid_client.command(cli_command)
        logger.debug('devstate change result: %s', result['response'][0])
