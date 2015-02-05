# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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

from __future__ import unicode_literals

import unittest
from xivo_agent.resources.agent.command import abstract


class ConcreteNoDataCommand(abstract.AbstractNoDataCommand):

    name = 'foobar'


class TestAbstractNoDataCommand(unittest.TestCase):

    def test_marshal(self):
        command = ConcreteNoDataCommand()

        msg = command.marshal()

        self.assertEqual(msg, None)

    def test_unmarshal(self):
        msg = None

        command = ConcreteNoDataCommand.unmarshal(msg)

        self.assertEqual(command.name, ConcreteNoDataCommand.name)


class ConcreteAgentIDCommand(abstract.AbstractAgentIDCommand):

    name = 'foo'


class TestAbstractAgentIDCommand(unittest.TestCase):

    def setUp(self):
        self.agent_id = 42
        self.msg = {'agent_id': self.agent_id}

    def test_marshal(self):
        command = ConcreteAgentIDCommand(self.agent_id)

        msg = command.marshal()

        self.assertEqual(msg, self.msg)

    def test_unmarshal(self):
        command = ConcreteAgentIDCommand.unmarshal(self.msg)

        self.assertEqual(command.name, ConcreteAgentIDCommand.name)
        self.assertEqual(command.agent_id, self.agent_id)


class ConcreteQueueIDCommand(abstract.AbstractQueueIDCommand):

    name = 'foo'


class TestAbstractQueueIDCommand(unittest.TestCase):

    def setUp(self):
        self.queue_id = 42
        self.msg = {'queue_id': self.queue_id}

    def test_marshal(self):
        command = ConcreteQueueIDCommand(self.queue_id)

        msg = command.marshal()

        self.assertEqual(msg, self.msg)

    def test_unmarshal(self):
        command = ConcreteQueueIDCommand.unmarshal(self.msg)

        self.assertEqual(command.name, ConcreteAgentIDCommand.name)
        self.assertEqual(command.queue_id, self.queue_id)


class ConcreteAgentAndQueueIDCommand(abstract.AbstractAgentAndQueueIDCommand):

    name = 'foo'


class TestAbstractAgentAndQueueIDCommand(unittest.TestCase):

    def setUp(self):
        self.agent_id = 1
        self.queue_id = 42
        self.msg = {'agent_id': self.agent_id, 'queue_id': self.queue_id}

    def test_marshal(self):
        command = ConcreteAgentAndQueueIDCommand(self.agent_id, self.queue_id)

        msg = command.marshal()

        self.assertEqual(msg, self.msg)

    def test_unmarshal(self):
        command = ConcreteAgentAndQueueIDCommand.unmarshal(self.msg)

        self.assertEqual(command.name, ConcreteAgentIDCommand.name)
        self.assertEqual(command.agent_id, self.agent_id)
        self.assertEqual(command.queue_id, self.queue_id)
