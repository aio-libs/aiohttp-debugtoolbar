import asyncio
from collections import deque
import datetime
import logging

from .base import DebugPanel
from ..utils import format_fname


class RequestTrackingHandler(logging.Handler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._records = deque(maxlen=1000)

    @property
    def records(self):
        return self._records

    def emit(self, record):
        self._records.append(record)


class LoggingPanel(DebugPanel):

    name = 'logging'
    template = 'logger.jinja2'
    title = 'Log Messages'
    nav_title = 'Logging'

    def __init__(self, request):
        super().__init__(request)
        self._log_handler = RequestTrackingHandler()

    def _install_handler(self):
        logging.root.addHandler(self._log_handler)

    def _uninstall_handler(self):
        logging.root.removeHandler(self._log_handler)

    def wrap_handler(self, handler, context_switcher):
        context_switcher.add_context_in(self._install_handler)
        context_switcher.add_context_out(self._uninstall_handler)
        return handler

    @asyncio.coroutine
    def process_response(self, response):
        records = []
        for record in self._log_handler.records:
            records.append({
                'message': record.getMessage(),
                'time': datetime.datetime.fromtimestamp(record.created),
                'level': record.levelname,
                'file': format_fname(record.pathname),
                'file_long': record.pathname,
                'line': record.lineno,
            })
        self.data = {'records': records}

    @property
    def has_content(self):
        if self.data.get('records'):
            return True
        return False

    @property
    def nav_subtitle(self):
        if self.data:
            return '%d' % len(self.data.get('records'))
