import aiohttp
import aiohttp_jinja2
import jinja2
from aiohttp import web

from aiohttp_debugtoolbar import middleware, setup as tbsetup

from ..base import BaseTest


class TestMiddleware(BaseTest):

    async def _setup_app(self, handler, **kw):
        app = web.Application(loop=self.loop,
                              middlewares=[middleware])

        tbsetup(app, **kw)

        tplt = "<html><body><h1>{{ head }}</h1>{{ text }}</body></html>"
        loader = jinja2.DictLoader({'tplt.html': tplt})
        aiohttp_jinja2.setup(app, loader=loader)

        app.router.add_route('GET', '/', handler)

        aio_handler = app.make_handler()
        srv = await self.loop.create_server(
            aio_handler, '127.0.0.1', self.port)
        return app, srv, aio_handler

    def test_handler_is_native_coroutine(self):

        async def func(request):
            resp = web.Response(body=b'native coroutine', status=200,
                                content_type='text/plain')
            return resp

        async def go():
            app, srv, handler = await self._setup_app(func)

            resp = await aiohttp.request('GET', self.url,
                                              loop=self.loop)
            self.assertEqual(200, resp.status)

            body = await resp.read()
            self.assertEquals(b'native coroutine', body)

            await handler.finish_connections()
            srv.close()

        self.loop.run_until_complete(go())