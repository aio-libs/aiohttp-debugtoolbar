import asyncio
import functools
import time
import inspect
from pprint import pformat

from aiohttp_debugtoolbar.panels.base import DebugPanel

from aioredis import RedisConnection


__all__ = ['RequestRedisDebugPanel']


class RequestRedisDebugPanel(DebugPanel):
    """
    A panel to display cache requests.
    """
    name = 'Redis'
    has_content = True
    template = 'request_redis.jinja2'
    title = 'Redis'
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
                # 'Active': Cache().is_active,
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
                    'command': args[1].decode("UTF-8").strip(),
                    'return': bool(context),
                    'key': args[2].strip(),
                    'params': {**{'args': args[4:]}, **dict(kwargs)},
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
            tmp = RedisConnection.execute
            RedisConnection.execute = wrapper(RedisConnection.execute)

            self._queries = []
            self.total_time = 0

            try:
                result = yield from handler(request)
            except:
                raise
            finally:
                # restore original
                RedisConnection.execute = tmp

            return result

        return timer_handler

    def wrap_handler(self, handler, context_switcher):
        handler = self._wrap_handler(handler)
        return handler
