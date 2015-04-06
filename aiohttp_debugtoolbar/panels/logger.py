import datetime
import logging

try:
    import threading
except ImportError:
    threading = None

from .base import DebugPanel
from ..utils import format_fname


_ = lambda x: x


raise NotImplementedError


class ThreadTrackingHandler(logging.Handler):
    def __init__(self):
        if threading is None:
            raise NotImplementedError(
                "threading module is not available, "
                "the logging panel cannot be used without it")
        logging.Handler.__init__(self)
        self.records = {}  # a dictionary that maps threads to log records

    def emit(self, record):
        self.get_records().append(record)

    def get_records(self, thread=None):
        """
        Returns a list of records for the provided thread, of if none is
        provided, returns a list for the current thread.
        """
        if thread is None:
            thread = threading.currentThread()
        if thread not in self.records:
            self.records[thread] = []
        return self.records[thread]

    def clear_records(self, thread=None):
        if thread is None:
            thread = threading.currentThread()
        if thread in self.records:
            del self.records[thread]


handler = ThreadTrackingHandler()
logging.root.addHandler(handler)


class LoggingPanel(DebugPanel):
    name = 'Logging'
    template = 'logger.dbtmako'
    title = _('Log Messages')
    nav_title = _('Logging')

    def __init__(self, request):
        handler.clear_records()

    def process_response(self, response):
        records = []
        for record in self.get_and_delete():
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
        else:
            return False

    def get_and_delete(self):
        records = handler.get_records()
        handler.clear_records()
        return records

    @property
    def nav_subtitle(self):
        if self.data:
            return '%d' % len(self.data.get('records'))
