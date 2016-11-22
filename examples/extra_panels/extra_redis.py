import asyncio
import functools
import time
import inspect

from aiohttp_debugtoolbar.panels.base import DebugPanel
from aioredis import RedisConnection

__all__ = ['RequestRedisDebugPanel']


class RequestHandler(object):
    def __init__(self):
        self._queries = []
        self._total_time = 0
        # save original
        self._tmp_execute = RedisConnection.execute

    @property
    def queries(self):
        return self._queries

    @property
    def total_time(self):
        return self._total_time

    def _wrapper(self, func):
        @functools.wraps(func)
        @asyncio.coroutine
        def wrapped(*args, **kwargs):
            start = time.time()

            if asyncio.iscoroutinefunction(func):
                coro = func
            else:
                coro = asyncio.coroutine(func)
            context = yield from coro(*args, **kwargs)

            called_from = []
            for stack in inspect.stack()[1:]:
                called_from.append("/{0}:{1}".format(
                    "/".join(stack[1].split('/')[-3:]), stack[2]))
                if len(called_from) >= 2:
                    break

            elapsed = time.time() - start
            arg = {
                'command': (args[1].decode("UTF-8").strip()
                            if isinstance(args[1], bytes) else args[1]),
                'return': bool(context),
                'key': args[2].strip(),
                'params': {**{'args': args[4:]}, **dict(kwargs)},
                'elapsed': '%0.3f sec' % elapsed,
                'called_from': "<br/>".join(reversed(called_from)),
            }
            self._queries.append(arg)
            self._total_time += elapsed

            return context

        return wrapped

    def on(self):
        RedisConnection.execute = self._wrapper(RedisConnection.execute)

    def off(self):
        RedisConnection.execute = self._tmp_execute


class RequestRedisDebugPanel(DebugPanel):
    """
    A panel to display cache requests.
    """
    name = 'Redis'
    template = 'request_redis.jinja2'
    title = 'Redis'
    nav_title = title

    def __init__(self, request):
        super().__init__(request)
        self._handler = RequestHandler()

    @property
    def has_content(self):
        if self.data.get('queries'):
            return True
        return False

    @asyncio.coroutine
    def process_response(self, response):
        self.data = data = {}
        data.update({
            'timing_rows': {
                'Total time': '%0.3f sec' % self._handler.total_time,
                'Total': len(self._handler.queries),
            }.items(),
            'queries': [(k, v) for k, v in enumerate(self._handler.queries)],
        })

    def _install_handler(self):
        self._handler.on()

    def _uninstall_handler(self):
        self._handler.off()

    def wrap_handler(self, handler, context_switcher):
        context_switcher.add_context_in(self._install_handler)
        context_switcher.add_context_out(self._uninstall_handler)
        return handler
