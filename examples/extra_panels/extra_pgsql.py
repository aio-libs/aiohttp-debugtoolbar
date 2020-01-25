import functools
import time
import inspect

from aiohttp_debugtoolbar.panels.base import DebugPanel
from aiopg.cursor import Cursor

__all__ = ['RequestPgDebugPanel']


class RequestHandler(object):
    def __init__(self):
        self._queries = []
        self._total_time = 0
        # save original
        self._tmp_execute = Cursor.execute

    @property
    def queries(self):
        return self._queries

    @property
    def total_time(self):
        return self._total_time

    def _wrapper(self, func):
        @functools.wraps(func)
        async def wrapped(*args, **kwargs):
            start = time.time()

            context = await func(*args, **kwargs)

            called_from = []
            for stack in inspect.stack()[1:]:
                called_from.append("/{0}:{1}".format(
                    "/".join(stack[1].split('/')[-3:]), stack[2]))
                if len(called_from) >= 2:
                    break

            elapsed = time.time() - start
            arg = {
                'query': args[1].strip().replace(
                    "\n", "<br>").replace(
                    "\t", "&nbsp;&nbsp;").replace(
                    "    ", "&nbsp;&nbsp;"),
                'params': args[2] if len(args) > 2 else [],
                'other': dict(kwargs),
                'elapsed': '%0.3f sec' % elapsed,
                'called_from': "<br/>".join(reversed(called_from)),
            }
            self._queries.append(arg)
            self._total_time += elapsed

            return context

        return wrapped

    def on(self):
        Cursor.execute = self._wrapper(Cursor.execute)

    def off(self):
        Cursor.execute = self._tmp_execute


class RequestPgDebugPanel(DebugPanel):
    """
    A panel to display SQL queries.
    """
    name = 'PgSQL'
    template = 'request_pgsql.jinja2'
    title = 'PgSQL Queries'
    nav_title = title

    def __init__(self, request):
        super().__init__(request)
        self._handler = RequestHandler()

    @property
    def has_content(self):
        if self.data.get('queries'):
            return True
        return False

    async def process_response(self, response):
        self.data = data = {}
        data.update({
            'timing_rows': {
                'Total time': '%0.3f sec' % self._handler.total_time,
                'Total': len(self._handler.queries),
            }.items(),
            'queries': [(k, v)
                        for k, v in enumerate(self._handler.queries)],
        })

    def _install_handler(self):
        self._handler.on()

    def _uninstall_handler(self):
        self._handler.off()

    def wrap_handler(self, handler, context_switcher):
        context_switcher.add_context_in(self._install_handler)
        context_switcher.add_context_out(self._uninstall_handler)
        return handler
