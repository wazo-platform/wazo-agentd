# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from functools import wraps


def agent(**agent):
    def _decorate(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            with self.database.queries() as queries:
                agent['id'] = queries.insert_agent(**agent)
            args = list(args) + [agent]
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
            args = list(args) + [queue]
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
                user_id, line_id, extension_id = queries.insert_user_line_extension(
                    **ule
                )
                ule['line_id'] = line_id
                ule['extension_id'] = line_id
                ule['user_id'] = user_id
            args = list(args) + [ule]
            try:
                return func(self, *args, **kwargs)
            finally:
                with self.database.queries() as queries:
                    queries.delete_user_line_extension(user_id, line_id, extension_id)

        return wrapper

    return _decorate
