import asyncio
import aiohttp
import pytest
import aiohttp_jinja2
import aiohttp_debugtoolbar
from aiohttp import web


@pytest.mark.run_loop
def test_render_toolbar_page(loop, create_server):
    @asyncio.coroutine
    def handler(request):
        return aiohttp_jinja2.render_template(
            'tplt.html', request,
            {'head': 'HEAD', 'text': 'text'})
    app, url = yield from create_server()
    app.router.add_route('GET', '/', handler)

    # make sure that toolbar button present on apps page
    # add cookie to enforce performance panel measure time
    conn = aiohttp.TCPConnector(loop=loop, force_close=True)
    cookie = {"pdtb_active": "pDebugPerformancePanel"}
    resp = yield from aiohttp.request('GET', url + '/', cookies=cookie,
                                      loop=loop, connector=conn)
    assert 200 == resp.status
    txt = yield from resp.text()
    assert 'pDebugToolbarHandle' in txt
    resp.close()

    # make sure that debug toolbar page working
    url = "{}/_debugtoolbar".format(url)
    resp = yield from aiohttp.request('GET', url, loop=loop, connector=conn)
    yield from resp.text()
    assert 200 == resp.status
    resp.close()
    conn.close()


@pytest.mark.run_loop
def test_render_with_exception(loop, create_server):
    @asyncio.coroutine
    def handler(request):
        raise NotImplementedError

    app, url = yield from create_server()
    app.router.add_route('GET', '/', handler)
    # make sure that exception page rendered
    resp = yield from aiohttp.request('GET', url + '/', loop=loop)
    txt = yield from resp.text()
    assert 500 == resp.status
    assert '<div class="debugger">' in txt


@pytest.mark.run_loop
def test_intercept_redirect(loop, create_server):
    @asyncio.coroutine
    def handler(request):
        raise web.HTTPMovedPermanently(location='/')

    app, url = yield from create_server()
    app.router.add_route('GET', '/', handler)
    # make sure that exception page rendered
    resp = yield from aiohttp.request(
        'GET', url + '/', allow_redirects=False, loop=loop)
    txt = yield from resp.text()
    assert 200 == resp.status
    assert 'Redirect intercepted' in txt


@pytest.mark.run_loop
def test_intercept_redirects_disabled(loop, create_server):
    @asyncio.coroutine
    def handler(request):
        raise web.HTTPMovedPermanently(location='/')

    app, url = yield from create_server(intercept_redirects=False)
    app.router.add_route('GET', '/', handler)
    # make sure that exception page rendered
    resp = yield from aiohttp.request(
        'GET', url + '/', allow_redirects=False, loop=loop)
    txt = yield from resp.text()
    assert 301 == resp.status
    assert '301: Moved Permanently' == txt


@pytest.mark.run_loop
def test_toolbar_not_enabled(loop, create_server):
    @asyncio.coroutine
    def handler(request):
        return aiohttp_jinja2.render_template(
            'tplt.html', request,
            {'head': 'HEAD', 'text': 'text'})

    app, url = yield from create_server(enabled=False)
    app.router.add_route('GET', '/', handler)
    # make sure that toolbar button NOT present on apps page
    resp = yield from aiohttp.request('GET', url + '/', loop=loop)
    assert 200 == resp.status
    txt = yield from resp.text()
    assert 'pDebugToolbarHandle' not in txt

    # make sure that debug toolbar page working
    url = "{}/_debugtoolbar".format(url)
    resp = yield from aiohttp.request('GET', url, loop=loop)
    yield from resp.text()
    assert 200 == resp.status


@pytest.mark.run_loop
def test_toolbar_content_type_json(loop, create_server):

    @asyncio.coroutine
    def handler(request):
        response = web.Response(status=200)
        response.content_type = 'application/json'
        response.text = '{"a": 42}'
        return response

    app, url = yield from create_server()
    app.router.add_route('GET', '/', handler)
    # make sure that toolbar button NOT present on apps page
    resp = yield from aiohttp.request('GET', url + '/', loop=loop)
    payload = yield from resp.json()
    assert 200 == resp.status
    assert payload == {"a": 42}


@pytest.mark.run_loop
def test_do_not_intercept_exceptions(loop, create_server):

    @asyncio.coroutine
    def handler(request):
        raise NotImplementedError

    app, url = yield from create_server(intercept_exc=False)
    app.router.add_route('GET', '/', handler)
    # make sure that exception page rendered
    resp = yield from aiohttp.request('GET', url + '/', loop=loop)
    txt = yield from resp.text()
    assert 500 == resp.status
    assert '<div class="debugger">' not in txt


@pytest.mark.run_loop
def test_setup_not_called_exception(loop):

    app = web.Application(loop=loop)
    with pytest.raises(RuntimeError):
        yield from aiohttp_debugtoolbar.middleware(app, lambda r: r)


@pytest.mark.run_loop
def test_process_stream_response(loop, create_server):
    @asyncio.coroutine
    def handler(request):
        response = web.StreamResponse(status=200)
        response.content_type = 'text/html'
        response.start(request)
        response.write(b'text')
        return response

    app, url = yield from create_server()
    app.router.add_route('GET', '/', handler)

    # make sure that toolbar button NOT present on apps page
    resp = yield from aiohttp.request('GET', url + '/', loop=loop)
    payload = yield from resp.read()
    assert 200 == resp.status
    assert payload == b'text'
