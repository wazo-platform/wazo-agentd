# Copyright 2019-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from functools import wraps


def agent(**agent):
    def _decorate(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            with self.database.queries() as queries:
                agent['id'] = queries.insert_agent(**agent)
            args = (*args, agent)
            try:
                return func(self, *args, **kwargs)
            finally:
                with self.database.queries() as queries:
                    queries.delete_agent(agent['id'])

        return wrapper

    return _decorate


def queue(**queue):
    def _decorate(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            with self.database.queries() as queries:
                queue['id'] = queries.insert_queue(**queue)
            args = (*args, queue)
            try:
                return func(self, *args, **kwargs)
            finally:
                with self.database.queries() as queries:
                    queries.delete_queue(queue['id'])

        return wrapper

    return _decorate


def user_line_extension(**ule):
    def _decorate(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            with self.database.queries() as queries:
                resource_ids = queries.insert_user_line_extension(**ule)
                ule.update(resource_ids)
            args = (*args, ule)
            try:
                return func(self, *args, **kwargs)
            finally:
                with self.database.queries() as queries:
                    queries.delete_user_line_extension(
                        resource_ids['user_id'],
                        resource_ids['line_id'],
                        resource_ids['extension_id'],
                    )

        return wrapper

    return _decorate
