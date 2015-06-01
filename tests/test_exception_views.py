import asyncio
import aiohttp
import aiohttp_jinja2
import jinja2
from aiohttp import web

from aiohttp_debugtoolbar import (middleware, setup as tbsetup, APP_KEY)

from .base import BaseTest


class TestExceptionViews(BaseTest):
    @asyncio.coroutine
    def _setup_app(self, handler, **kw):
        app = web.Application(loop=self.loop,
                              middlewares=[middleware])

        tbsetup(app, **kw)

        tplt = "<html><body><h1>{{ head }}</h1>{{ text }}</body></html>"
        loader = jinja2.DictLoader({'tplt.html': tplt})
        aiohttp_jinja2.setup(app, loader=loader)
        app.router.add_route('GET', '/', handler)

        handler = app.make_handler()
        srv = yield from self.loop.create_server(
            handler, '127.0.0.1', self.port)
        return app, srv, handler

    def test_view_source(self):
        @asyncio.coroutine
        def func(request):
            raise NotImplementedError

        @asyncio.coroutine
        def go():
            app, srv, handler = yield from self._setup_app(func)
            # make sure that exception page rendered
            resp = yield from aiohttp.request('GET', self.url, loop=self.loop)
            txt = yield from resp.text()
            self.assertEqual(500, resp.status)
            self.assertTrue('<div class="debugger">' in txt)

            token = app[APP_KEY]['pdtb_token']
            exc_history = app[APP_KEY]['exc_history']

            for frame_id in exc_history.frames:
                url = '{}/_debugtoolbar/source?frm={}&token={}'.format(
                    self.url, frame_id, token)
                exc_history = app[APP_KEY]['exc_history']
                resp = yield from aiohttp.request('GET', url,
                                                  loop=self.loop)
                yield from resp.text()
                self.assertEqual(resp.status, 200)

            yield from handler.finish_connections()
            srv.close()

        self.loop.run_until_complete(go())

    def test_view_execute(self):
        @asyncio.coroutine
        def func(request):
            raise NotImplementedError

        @asyncio.coroutine
        def go():
            app, srv, handler = yield from self._setup_app(func)
            # make sure that exception page rendered
            resp = yield from aiohttp.request('GET', self.url, loop=self.loop)
            txt = yield from resp.text()
            self.assertEqual(500, resp.status)
            self.assertTrue('<div class="debugger">' in txt)

            token = app[APP_KEY]['pdtb_token']
            exc_history = app[APP_KEY]['exc_history']

            for frame_id in exc_history.frames:
                params = {'frm': frame_id, 'token': token}
                url = '{}/_debugtoolbar/source'.format(self.url)
                resp = yield from aiohttp.request('GET', url, params=params,
                                                  loop=self.loop)
                yield from resp.text()
                self.assertEqual(resp.status, 200)

                params = {'frm': frame_id, 'token': token,
                          'cmd': 'dump(object)'}
                url = '{}/_debugtoolbar/execute'.format(self.url)
                resp = yield from aiohttp.request('GET', url, params=params,
                                                  loop=self.loop)
                yield from resp.text()
                self.assertEqual(resp.status, 200)

            # wrong token
            params = {'frm': frame_id, 'token': 'x', 'cmd': 'dump(object)'}
            resp = yield from aiohttp.request('GET', url, params=params,
                                              loop=self.loop)
            self.assertEqual(resp.status, 400)
            # no token at all
            params = {'frm': frame_id, 'cmd': 'dump(object)'}
            resp = yield from aiohttp.request('GET', url, params=params,
                                              loop=self.loop)
            self.assertEqual(resp.status, 400)

            yield from handler.finish_connections()
            srv.close()

        self.loop.run_until_complete(go())

    def test_view_exception(self):
        @asyncio.coroutine
        def func(request):
            raise NotImplementedError

        @asyncio.coroutine
        def go():
            app, srv, handler = yield from self._setup_app(func)
            # make sure that exception page rendered
            resp = yield from aiohttp.request('GET', self.url, loop=self.loop)
            txt = yield from resp.text()
            self.assertEqual(500, resp.status)
            self.assertTrue('<div class="debugger">' in txt)

            token = app[APP_KEY]['pdtb_token']
            exc_history = app[APP_KEY]['exc_history']

            tb_id = list(exc_history.tracebacks.keys())[0]
            url = '{}/_debugtoolbar/exception?tb={}&token={}'.format(
                self.url, tb_id, token)

            resp = yield from aiohttp.request('GET', url,
                                              loop=self.loop)
            yield from resp.text()
            self.assertEqual(resp.status, 200)
            self.assertTrue('<div class="debugger">' in txt)

            yield from handler.finish_connections()
            srv.close()

        self.loop.run_until_complete(go())
