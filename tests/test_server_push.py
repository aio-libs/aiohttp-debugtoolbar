import asyncio
import json
import aiohttp
import aiohttp_jinja2
import jinja2
from aiohttp import web

from aiohttp_debugtoolbar import middleware, setup as tbsetup, APP_KEY

from .base import BaseTest


class TestExceptionViews(BaseTest):
    @asyncio.coroutine
    def _setup_app(self, handler, **kw):
        app = web.Application(loop=self.loop, middlewares=[middleware])

        tbsetup(app, **kw)

        tplt = "<html><body><h1>{{ head }}</h1>{{ text }}</body></html>"
        loader = jinja2.DictLoader({'tplt.html': tplt})
        aiohttp_jinja2.setup(app, loader=loader)

        app.router.add_route('GET', '/', handler)
        app_handler = app.make_handler()
        srv = yield from self.loop.create_server(
            app_handler, '127.0.0.1', self.port)
        return app, srv, app_handler

    def test_sse(self):
        @asyncio.coroutine
        def func(request):
            raise NotImplementedError

        @asyncio.coroutine
        def go():
            app, srv, app_handler = yield from self._setup_app(func)
            # make sure that exception page rendered
            resp = yield from aiohttp.request('GET', self.url, loop=self.loop)
            txt = yield from resp.text()
            self.assertEqual(500, resp.status)
            self.assertTrue('<div class="debugger">' in txt)

            # get request id from history
            history = app[APP_KEY]['request_history']
            request_id = history[0][0]

            url = '{}/_debugtoolbar/sse'.format(self.url)
            resp = yield from aiohttp.request('GET', url, loop=self.loop)
            data = yield from resp.text()
            data = data.strip()

            # split and check EventSource data
            event_id, event, payload_raw = data.split('\n')
            self.assertEqual(event_id, 'id: {}'.format(request_id))
            self.assertEqual(event, 'event: new_request')

            payload_json = payload_raw.strip('data: ')
            payload = json.loads(payload_json)
            expected = [[request_id, {"path": "/",
                                      "scheme": "http",
                                      "method": "GET",
                                      "status_code": 500},
                         ""]]

            self.assertEqual(payload, expected, payload)
            yield from app_handler.finish_connections(timeout=600)
            srv.close()
            yield from srv.wait_closed()

        self.loop.run_until_complete(go())
