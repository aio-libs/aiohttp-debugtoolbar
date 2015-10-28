import asyncio
import aiohttp

from aiohttp_debugtoolbar import APP_KEY


def test_view_source(loop, create_server):
    @asyncio.coroutine
    def handler(request):
        raise NotImplementedError

    @asyncio.coroutine
    def go():
        app, url = yield from create_server()
        app.router.add_route('GET', '/', handler)

        # make sure that exception page rendered
        resp = yield from aiohttp.request('GET', url + '/', loop=loop)
        txt = yield from resp.text()
        assert 500 == resp.status
        assert '<div class="debugger">' in txt

        token = app[APP_KEY]['pdtb_token']
        exc_history = app[APP_KEY]['exc_history']

        for frame_id in exc_history.frames:
            source_url = '{}/_debugtoolbar/source?frm={}&token={}'.format(
                url, frame_id, token)
            exc_history = app[APP_KEY]['exc_history']
            resp = yield from aiohttp.request('GET', source_url, loop=loop)
            yield from resp.text()
            assert resp.status == 200

    loop.run_until_complete(go())


def test_view_execute(loop, create_server):
    @asyncio.coroutine
    def handler(request):
        raise NotImplementedError

    @asyncio.coroutine
    def go():
        app, url = yield from create_server()
        app.router.add_route('GET', '/', handler)
        # make sure that exception page rendered
        resp = yield from aiohttp.request('GET', url + '/', loop=loop)
        txt = yield from resp.text()
        assert 500 == resp.status
        assert '<div class="debugger">' in txt

        token = app[APP_KEY]['pdtb_token']
        exc_history = app[APP_KEY]['exc_history']

        source_url = '{}/_debugtoolbar/source'.format(url)
        execute_url = '{}/_debugtoolbar/execute'.format(url)
        for frame_id in exc_history.frames:
            params = {'frm': frame_id, 'token': token}
            resp = yield from aiohttp.request('GET', source_url, params=params,
                                              loop=loop)
            yield from resp.text()
            assert resp.status == 200

            params = {'frm': frame_id, 'token': token,
                      'cmd': 'dump(object)'}
            resp = yield from aiohttp.request('GET', execute_url,
                                              params=params, loop=loop)
            yield from resp.text()
            assert resp.status == 200

        # wrong token
        params = {'frm': frame_id, 'token': 'x', 'cmd': 'dump(object)'}
        resp = yield from aiohttp.request('GET', execute_url, params=params,
                                          loop=loop)
        assert resp.status == 400
        # no token at all
        params = {'frm': frame_id, 'cmd': 'dump(object)'}
        resp = yield from aiohttp.request('GET', execute_url, params=params,
                                          loop=loop)
        assert resp.status == 400

    loop.run_until_complete(go())


def test_view_exception(loop, create_server):
    @asyncio.coroutine
    def handler(request):
        raise NotImplementedError

    @asyncio.coroutine
    def go():
        app, url = yield from create_server()
        app.router.add_route('GET', '/', handler)
        # make sure that exception page rendered
        resp = yield from aiohttp.request('GET', url + '/', loop=loop)
        txt = yield from resp.text()
        assert 500 == resp.status
        assert '<div class="debugger">' in txt

        token = app[APP_KEY]['pdtb_token']
        exc_history = app[APP_KEY]['exc_history']

        tb_id = list(exc_history.tracebacks.keys())[0]
        url = '{}/_debugtoolbar/exception?tb={}&token={}'.format(
            url, tb_id, token)

        resp = yield from aiohttp.request('GET', url,
                                          loop=loop)
        yield from resp.text()
        assert resp.status == 200
        assert '<div class="debugger">' in txt

    loop.run_until_complete(go())
