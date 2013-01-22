# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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

import unittest
from mock import patch, ANY
from xivo_agent import config
from xivo_agent.db_manager import DBManager


class TestDBManager(unittest.TestCase):

    @patch('xivo_dao.alchemy.dbconnection.register_db_connection_pool')
    @patch('xivo_dao.alchemy.dbconnection.add_connection_as')
    def test_connect(self, add_connection_as, register_db_connection_pool):
        db_manager = DBManager()

        db_manager.connect()

        register_db_connection_pool.assert_called_once_with(ANY)
        add_connection_as.assert_called_once_with(config.DB_URI, 'asterisk')

    @patch('xivo_dao.alchemy.dbconnection.unregister_db_connection_pool')
    def test_disconnect(self, unregister_db_connection_pool):
        db_manager = DBManager()

        db_manager.disconnect()

        unregister_db_connection_pool.assert_called_once_with()

    def test_reconnect(self):
        db_manager = DBManager()

        with patch.object(db_manager, 'disconnect') as disconnect:
            with patch.object(db_manager, 'connect') as connect:
                db_manager.reconnect()

                disconnect.assert_called_once_with()
                connect.assert_called_once_with()
