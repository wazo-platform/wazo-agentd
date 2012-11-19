# -*- coding: UTF-8 -*-

from xivo_agent.ami.actions.common.action import BaseAction


class DBGetAction(BaseAction):

    def __init__(self, family, key):
        BaseAction.__init__(self, 'DBGet', [
            ('Family', family),
            ('Key', key),
        ])
        self._val = None

    @property
    def val(self):
        self.wait_for_completion()
        return self._val

    def _on_response_received(self, response):
        if not response.is_success():
            self._completed = True

    def _on_event_received(self, event):
        if event.name == 'DBGetComplete':
            self._completed = True
        elif event.name == 'DBGetResponse':
            self._val = event.get_value('Val')
            self._completed = True
        else:
            raise Exception('unexpected event %r' % event)
