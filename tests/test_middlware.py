import asyncio
import aiohttp
import aiohttp_mako
from aiohttp import web

from aiohttp_debugtoolbar import toolbar_middleware_factory, setup as tbsetup

from .base import BaseTest


class TestMiddleware(BaseTest):

    @asyncio.coroutine
    def _setup_app(self, handler, **kw):
        app = web.Application(loop=self.loop,
                              middlewares=[toolbar_middleware_factory])

        tbsetup(app, **kw)
        lookup = aiohttp_mako.setup(app, input_encoding='utf-8',
                                    output_encoding='utf-8',
                                    default_filters=['decode.utf8'])
        tplt = "<html><body><h1>${head}</h1>${text}</body></html>"
        lookup.put_string('tplt.html', tplt)

        app.router.add_route('GET', '/', handler)

        handler = app.make_handler()
        srv = yield from self.loop.create_server(
            handler, '127.0.0.1', self.port)
        return app, srv, handler

    def test_render_toolbar_page(self):
        @asyncio.coroutine
        def func(request):
            return aiohttp_mako.render_template(
                'tplt.html', request,
                {'head': 'HEAD', 'text': 'text'})

        @asyncio.coroutine
        def go():
            app, srv, handler = yield from self._setup_app(func)

            # make sure that toolbar button present on apps page
            # add cookie to enforce performance panel measure time
            conn = aiohttp.TCPConnector(loop=self.loop, force_close=True)
            cookie = {"pdtb_active": "pDebugPerformancePanel"}
            resp = yield from aiohttp.request('GET', self.url, cookies=cookie,
                                              loop=self.loop, connector=conn)
            self.assertEqual(200, resp.status)
            txt = yield from resp.text()
            self.assertTrue('pDebugToolbarHandle' in txt)
            resp.close()

            # make sure that debug toolbar page working
            url = "{}/_debugtoolbar".format(self.url)
            resp = yield from aiohttp.request('GET', url, loop=self.loop,
                                              connector=conn)
            yield from resp.text()
            self.assertEqual(200, resp.status)
            resp.close()

            conn.close()

            yield from handler.finish_connections()
            srv.close()

        self.loop.run_until_complete(go())

    def test_render_with_exception(self):
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

            yield from handler.finish_connections()
            srv.close()

        self.loop.run_until_complete(go())

    def test_intercept_redirect(self):
        @asyncio.coroutine
        def func(request):
            raise web.HTTPMovedPermanently(location='/')

        @asyncio.coroutine
        def go():
            app, srv, handler = yield from self._setup_app(func)

            # make sure that exception page rendered
            resp = yield from aiohttp.request(
                'GET', self.url, allow_redirects=False, loop=self.loop)
            txt = yield from resp.text()
            self.assertEqual(200, resp.status)
            self.assertTrue('Redirect intercepted' in txt)

            yield from handler.finish_connections()
            srv.close()

        self.loop.run_until_complete(go())

    def test_intercept_redirects_disabled(self):
        @asyncio.coroutine
        def func(request):
            raise web.HTTPMovedPermanently(location='/')

        @asyncio.coroutine
        def go():
            app, srv, handler = yield from self._setup_app(
                func, intercept_redirects=False)

            # make sure that exception page rendered
            resp = yield from aiohttp.request(
                'GET', self.url, allow_redirects=False, loop=self.loop)
            txt = yield from resp.text()
            self.assertEqual(301, resp.status)
            self.assertEqual('301: Moved Permanently', txt)

            yield from handler.finish_connections()
            srv.close()

        self.loop.run_until_complete(go())

    def test_toolbar_not_enabled(self):
        @asyncio.coroutine
        def func(request):
            return aiohttp_mako.render_template(
                'tplt.html', request,
                {'head': 'HEAD', 'text': 'text'})

        @asyncio.coroutine
        def go():
            app, srv, handler = yield from self._setup_app(func, enabled=False)

            # make sure that toolbar button NOT present on apps page
            resp = yield from aiohttp.request('GET', self.url, loop=self.loop)
            self.assertEqual(200, resp.status)
            txt = yield from resp.text()
            self.assertFalse('pDebugToolbarHandle' in txt)

            # make sure that debug toolbar page working
            url = "{}/_debugtoolbar".format(self.url)
            resp = yield from aiohttp.request('GET', url, loop=self.loop)
            yield from resp.text()
            self.assertEqual(200, resp.status)

            yield from handler.finish_connections()
            srv.close()

        self.loop.run_until_complete(go())

    def test_toolbar_content_type_json(self):

        @asyncio.coroutine
        def func(request):
            response = web.Response(status=200)
            response.content_type = 'application/json'
            response.text = '{"a": 42}'
            return response

        @asyncio.coroutine
        def go():
            app, srv, handler = yield from self._setup_app(func)

            # make sure that toolbar button NOT present on apps page
            resp = yield from aiohttp.request('GET', self.url, loop=self.loop)
            payload = yield from resp.json()
            self.assertEqual(200, resp.status)
            self.assertEqual(payload, {"a": 42})

            yield from handler.finish_connections()
            srv.close()

        self.loop.run_until_complete(go())

    def test_do_not_intercept_exceptions(self):

        @asyncio.coroutine
        def func(request):
            raise NotImplementedError

        @asyncio.coroutine
        def go():
            app, srv, handler = yield from self._setup_app(
                func, intercept_exc=False)
            # make sure that exception page rendered
            resp = yield from aiohttp.request('GET', self.url, loop=self.loop)
            txt = yield from resp.text()
            self.assertEqual(500, resp.status)
            self.assertFalse('<div class="debugger">' in txt)

            yield from handler.finish_connections()
            srv.close()

        self.loop.run_until_complete(go())

    def test_setup_not_called_exception(self):

        @asyncio.coroutine
        def go():
            app = web.Application(loop=self.loop)
            with self.assertRaises(RuntimeError):
                yield from toolbar_middleware_factory(app, lambda r: r)

        self.loop.run_until_complete(go())
