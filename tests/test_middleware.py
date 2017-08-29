import asyncio
import pytest
import aiohttp_jinja2
import aiohttp_debugtoolbar
from aiohttp import web


@asyncio.coroutine
def test_render_toolbar_page(create_server, test_client):
    @asyncio.coroutine
    def handler(request):
        return aiohttp_jinja2.render_template(
            'tplt.html', request,
            {'head': 'HEAD', 'text': 'text'})

    app = yield from create_server()
    app.router.add_route('GET', '/', handler)
    cookie = {"pdtb_active": "pDebugPerformancePanel"}
    client = yield from test_client(app, cookies=cookie)

    # make sure that toolbar button present on apps page
    # add cookie to enforce performance panel measure time
    resp = yield from client.get('/')
    assert 200 == resp.status
    txt = yield from resp.text()
    assert 'toolbar_button.css' in txt
    assert 'pDebugToolbarHandle' in txt

    # make sure that debug toolbar page working
    url = "/_debugtoolbar"
    resp = yield from client.get(url)
    yield from resp.text()
    assert 200 == resp.status


@asyncio.coroutine
def test_render_with_exception(create_server, test_client):
    @asyncio.coroutine
    def handler(request):
        raise NotImplementedError

    app = yield from create_server()
    app.router.add_route('GET', '/', handler)
    client = yield from test_client(app)
    # make sure that exception page rendered
    resp = yield from client.get('/')
    txt = yield from resp.text()
    assert 500 == resp.status
    assert '<div class="debugger">' in txt


@asyncio.coroutine
def test_intercept_redirect(create_server, test_client):
    @asyncio.coroutine
    def handler(request):
        raise web.HTTPMovedPermanently(location='/')

    app = yield from create_server()
    app.router.add_route('GET', '/', handler)
    client = yield from test_client(app)
    # make sure that exception page rendered
    resp = yield from client.get('/', allow_redirects=False)
    txt = yield from resp.text()
    assert 200 == resp.status
    assert 'Redirect intercepted' in txt


@asyncio.coroutine
def test_no_location_no_intercept(create_server, test_client):

    @asyncio.coroutine
    def handler(request):
        return web.Response(text="no location", status=301)

    app = yield from create_server()
    app.router.add_route('GET', '/', handler)
    client = yield from test_client(app)

    resp = yield from client.get('/', allow_redirects=False)
    txt = yield from resp.text()
    assert 301 == resp.status
    assert 'location' not in resp.headers
    assert 'no location' in txt


@asyncio.coroutine
def test_intercept_redirects_disabled(create_server, test_client):
    @asyncio.coroutine
    def handler(request):
        raise web.HTTPMovedPermanently(location='/')

    app = yield from create_server(intercept_redirects=False)
    app.router.add_route('GET', '/', handler)
    client = yield from test_client(app)
    # make sure that exception page rendered
    resp = yield from client.get('/', allow_redirects=False)
    txt = yield from resp.text()
    assert 301 == resp.status
    assert '301: Moved Permanently' == txt


@asyncio.coroutine
def test_toolbar_not_enabled(create_server, test_client):
    @asyncio.coroutine
    def handler(request):
        return aiohttp_jinja2.render_template(
            'tplt.html', request,
            {'head': 'HEAD', 'text': 'text'})

    app = yield from create_server(enabled=False)
    app.router.add_route('GET', '/', handler)
    client = yield from test_client(app)
    # make sure that toolbar button NOT present on apps page
    resp = yield from client.get('/')
    assert 200 == resp.status
    txt = yield from resp.text()
    assert 'pDebugToolbarHandle' not in txt

    # make sure that debug toolbar page working
    url = "/_debugtoolbar"
    resp = yield from client.get(url)
    yield from resp.text()
    assert 200 == resp.status


@asyncio.coroutine
def test_toolbar_content_type_json(create_server, test_client):

    @asyncio.coroutine
    def handler(request):
        response = web.Response(status=200)
        response.content_type = 'application/json'
        response.text = '{"a": 42}'
        return response

    app = yield from create_server()
    app.router.add_route('GET', '/', handler)
    client = yield from test_client(app)
    # make sure that toolbar button NOT present on apps page
    resp = yield from client.get('/')
    payload = yield from resp.json()
    assert 200 == resp.status
    assert payload == {"a": 42}


@asyncio.coroutine
def test_do_not_intercept_exceptions(create_server, test_client):

    @asyncio.coroutine
    def handler(request):
        raise NotImplementedError

    app = yield from create_server(intercept_exc=False)
    app.router.add_route('GET', '/', handler)
    client = yield from test_client(app)
    # make sure that exception page rendered
    resp = yield from client.get('/')
    txt = yield from resp.text()
    assert 500 == resp.status
    assert '<div class="debugger">' not in txt


@asyncio.coroutine
def test_setup_not_called_exception(loop):

    app = web.Application(loop=loop)
    with pytest.raises(RuntimeError):
        yield from aiohttp_debugtoolbar.middleware(app, lambda r: r)


def test_setup_only_adds_middleware_if_not_already_added(loop):
    app = web.Application(loop=loop,
                          middlewares=[aiohttp_debugtoolbar.middleware])
    aiohttp_debugtoolbar.setup(app)
    assert list(app.middlewares) == [aiohttp_debugtoolbar.middleware]


@asyncio.coroutine
def test_process_stream_response(create_server, test_client):
    @asyncio.coroutine
    def handler(request):
        response = web.StreamResponse(status=200)
        response.content_type = 'text/html'
        yield from response.prepare(request)
        response.write(b'text')
        return response

    app = yield from create_server()
    app.router.add_route('GET', '/', handler)
    client = yield from test_client(app)

    # make sure that toolbar button NOT present on apps page
    resp = yield from client.get('/')
    payload = yield from resp.read()
    assert 200 == resp.status
    assert payload == b'text'
