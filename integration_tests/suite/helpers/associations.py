# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from contextlib import contextmanager


@contextmanager
def user_agent(database, user_id, agent_id, check=True):
    with database.queries() as queries:
        queries.associate_user_agent(user_id, agent_id)
        yield
        queries.dissociate_user_agent(user_id, agent_id)
