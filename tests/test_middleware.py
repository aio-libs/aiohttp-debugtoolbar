import asyncio

import aiohttp_jinja2
import pytest
from aiohttp import web
from aiohttp.test_utils import make_mocked_request

import aiohttp_debugtoolbar


async def test_render_toolbar_page(create_server, aiohttp_client):
    async def handler(request):
        return aiohttp_jinja2.render_template(
            "tplt.html", request, {"head": "HEAD", "text": "text"}
        )

    app = await create_server()
    app.router.add_route("GET", "/", handler)
    cookie = {"pdtb_active": "pDebugPerformancePanel"}
    client = await aiohttp_client(app, cookies=cookie)

    # make sure that toolbar button present on apps page
    # add cookie to enforce performance panel measure time
    resp = await client.get("/")
    assert 200 == resp.status
    txt = await resp.text()
    assert "toolbar_button.css" in txt
    assert "pDebugToolbarHandle" in txt

    # make sure that debug toolbar page working
    url = "/_debugtoolbar"
    resp = await client.get(url)
    await resp.text()
    assert 200 == resp.status


async def test_render_with_exception(create_server, aiohttp_client):
    async def handler(request):
        raise NotImplementedError

    app = await create_server()
    app.router.add_route("GET", "/", handler)
    client = await aiohttp_client(app)
    # make sure that exception page rendered
    resp = await client.get("/")
    txt = await resp.text()
    assert 500 == resp.status
    assert '<div class="debugger">' in txt


async def test_intercept_redirect(create_server, aiohttp_client):
    async def handler(request):
        raise web.HTTPMovedPermanently(location="/")

    app = await create_server()
    app.router.add_route("GET", "/", handler)
    client = await aiohttp_client(app)
    # make sure that exception page rendered
    resp = await client.get("/", allow_redirects=False)
    txt = await resp.text()
    assert 200 == resp.status
    assert "Redirect intercepted" in txt


async def test_no_location_no_intercept(create_server, aiohttp_client):
    async def handler(request):
        return web.Response(text="no location", status=301)

    app = await create_server()
    app.router.add_route("GET", "/", handler)
    client = await aiohttp_client(app)

    resp = await client.get("/", allow_redirects=False)
    txt = await resp.text()
    assert 301 == resp.status
    assert "location" not in resp.headers
    assert "no location" in txt


async def test_intercept_redirects_disabled(create_server, aiohttp_client):
    async def handler(request):
        raise web.HTTPMovedPermanently(location="/")

    app = await create_server(intercept_redirects=False)
    app.router.add_route("GET", "/", handler)
    client = await aiohttp_client(app)
    # make sure that exception page rendered
    resp = await client.get("/", allow_redirects=False)
    txt = await resp.text()
    assert 301 == resp.status
    assert "301: Moved Permanently" == txt


async def test_toolbar_not_enabled(create_server, aiohttp_client):
    async def handler(request):
        return aiohttp_jinja2.render_template(
            "tplt.html", request, {"head": "HEAD", "text": "text"}
        )

    app = await create_server(enabled=False)
    app.router.add_route("GET", "/", handler)
    client = await aiohttp_client(app)
    # make sure that toolbar button NOT present on apps page
    resp = await client.get("/")
    assert 200 == resp.status
    txt = await resp.text()
    assert "pDebugToolbarHandle" not in txt

    # make sure that debug toolbar page working
    url = "/_debugtoolbar"
    resp = await client.get(url)
    await resp.text()
    assert 200 == resp.status


async def test_toolbar_content_type_json(create_server, aiohttp_client):
    async def handler(request):
        response = web.Response(status=200)
        response.content_type = "application/json"
        response.text = '{"a": 42}'
        return response

    app = await create_server()
    app.router.add_route("GET", "/", handler)
    client = await aiohttp_client(app)
    # make sure that toolbar button NOT present on apps page
    resp = await client.get("/")
    payload = await resp.json()
    assert 200 == resp.status
    assert payload == {"a": 42}


async def test_do_not_intercept_exceptions(create_server, aiohttp_client):
    async def handler(request):
        raise NotImplementedError

    app = await create_server(intercept_exc=False)
    app.router.add_route("GET", "/", handler)
    client = await aiohttp_client(app)
    # make sure that exception page rendered
    resp = await client.get("/")
    txt = await resp.text()
    assert 500 == resp.status
    assert '<div class="debugger">' not in txt


async def test_setup_not_called_exception():
    request = make_mocked_request("GET", "/path")
    with pytest.raises(RuntimeError):
        await aiohttp_debugtoolbar.middleware(request, lambda r: r)


async def test_setup_only_adds_middleware_if_not_already_added():
    app = web.Application(middlewares=[aiohttp_debugtoolbar.middleware])
    aiohttp_debugtoolbar.setup(app)
    assert list(app.middlewares) == [aiohttp_debugtoolbar.middleware]


async def test_process_stream_response(create_server, aiohttp_client):
    async def handler(request):
        response = web.StreamResponse(status=200)
        response.content_type = "text/html"
        await response.prepare(request)
        await response.write(b"text")
        return response

    app = await create_server()
    app.router.add_route("GET", "/", handler)
    client = await aiohttp_client(app)

    # make sure that toolbar button NOT present on apps page
    resp = await client.get("/")
    payload = await resp.read()
    assert 200 == resp.status
    assert payload == b"text"


async def test_performance_panel_with_handler(create_server, aiohttp_client):
    async def handler(request):
        return web.Response()

    app = await create_server()
    app.router.add_route("GET", "/", handler)
    client = await aiohttp_client(app)

    resp = await client.get("/")
    assert 200 == resp.status


async def test_performance_panel_with_cbv(create_server, aiohttp_client):
    class TestView(web.View):
        async def get(self):
            return web.Response()

    app = await create_server()
    app.router.add_view("/", TestView)
    client = await aiohttp_client(app)

    resp = await client.get("/")
    assert 200 == resp.status


async def test_request_history(create_server, aiohttp_client):
    async def handler(request: web.Request) -> web.Response:
        return web.Response()

    app = await create_server(check_host=False)
    app.router.add_route("GET", "/", handler)
    app.router.add_route("GET", "/favicon.ico", handler)
    client = await aiohttp_client(app)

    # Should be logged
    async with client.get("/") as r:
        assert r.status == 200
    # Should not be logged
    async with client.get("/favicon.ico") as r:
        assert r.status == 200
    async with client.get("/_debugtoolbar/static/img/aiohttp.svg") as r:
        assert r.status == 200

    request_history = tuple(app[aiohttp_debugtoolbar.APP_KEY]["request_history"])
    assert len(request_history) == 1
    assert request_history[0][1].request.path == "/"

    await asyncio.sleep(0)  # Workaround, maybe fixed in aiohttp 4.
