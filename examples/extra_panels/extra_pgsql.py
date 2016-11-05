import asyncio
import functools
import time
import inspect

from aiohttp_debugtoolbar.panels.base import DebugPanel

from aiopg.cursor import Cursor


__all__ = ['RequestPgDebugPanel']


class RequestPgDebugPanel(DebugPanel):
    """
    A panel to display SQL queries.
    """
    name = 'PgSQL'
    has_content = True
    template = 'request_pgsql.jinja2'
    title = 'PgSQL Queries'
    nav_title = title
    _original_func = None

    def __init__(self, request):
        super().__init__(request)

    @asyncio.coroutine
    def process_response(self, response):
        self.data = data = {}
        data.update({
            'timing_rows': {
                'Total time': '%0.3f sec' % self.total_time,
                'Total': len(self._queries),
            }.items(),
            'queries': [(k, v) for k, v in enumerate(self._queries)],
        })

    def _wrap_handler(self, handler):

        def wrapper(func):
            @functools.wraps(func)
            async def wrapped(*args, **kwargs):
                start = time.time()

                if asyncio.iscoroutinefunction(func):
                    coro = func
                else:
                    coro = asyncio.coroutine(func)
                context = await coro(*args, **kwargs)

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
                self.total_time += elapsed

                return context

            return wrapped

        @asyncio.coroutine
        def timer_handler(request):
            # save original
            tmp_query = Cursor.execute
            Cursor.execute = wrapper(Cursor.execute)

            self._queries = []
            self.total_time = 0

            try:
                result = yield from handler(request)
            except:
                raise
            finally:
                # restore original
                Cursor.execute = tmp_query

            return result

        return timer_handler

    def wrap_handler(self, handler, context_switcher):
        handler = self._wrap_handler(handler)
        return handler
