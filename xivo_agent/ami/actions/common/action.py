# -*- coding: utf-8 -*-
# Copyright (C) 2012-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+


class BaseAction(object):

    def __init__(self, name, headers):
        self._name = name
        self._lines = self._format_headers(headers)
        # package private attributes
        self._action_id = None
        self._amiclient = None
        self._completed = False
        self._response = None

    def _format_headers(self, headers):
        return ['%s: %s' % (header, value) for (header, value) in headers if
                value is not None]

    def format(self):
        lines = ['Action: %s' % self._name]
        if self._action_id is not None:
            lines.append('ActionID: %s' % self._action_id)
        lines.extend(self._lines)
        lines.append('\r\n')
        return '\r\n'.join(lines).encode('UTF-8')

    @property
    def success(self):
        self.wait_for_completion()
        return self._response.is_success()

    def wait_for_completion(self):
        if not self._completed:
            self._amiclient.wait_for_completion(self)

    # package private method
    def _on_response_received(self, response):
        # may be overridden
        self._completed = True

    # package private method
    def _on_event_received(self, event):
        # may be overridden
        pass
