import asyncio
import socket
import sys

import pytest
import jinja2
import aiohttp_jinja2
from aiohttp import web
from aiohttp_debugtoolbar import middleware, setup


def pytest_ignore_collect(path, config):
    if 'pep492' in str(path):
        if sys.version_info < (3, 5, 0):
            return True


@pytest.fixture
def unused_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()
    return port


@pytest.fixture
def loop(request):
    try:
        old_loop = asyncio.get_event_loop()
    except RuntimeError:
        old_loop = None
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(None)

    def fin():
        loop.close()
        asyncio.set_event_loop(old_loop)

    request.addfinalizer(fin)
    return loop


@pytest.yield_fixture
def create_server(loop, unused_port):
    app = app_handler = srv = None

    @asyncio.coroutine
    def create(*, debug=False, ssl_ctx=None, **kw):
        nonlocal app, app_handler, srv
        app = web.Application(loop=loop, middlewares=[middleware])
        setup(app, **kw)
        port = unused_port

        tplt = "<html><body><h1>{{ head }}</h1>{{ text }}</body></html>"
        loader = jinja2.DictLoader({'tplt.html': tplt})
        aiohttp_jinja2.setup(app, loader=loader)

        app_handler = app.make_handler(debug=debug, keep_alive_on=False)
        srv = yield from loop.create_server(app_handler, '127.0.0.1', port,
                                            ssl=ssl_ctx)
        proto = "https" if ssl_ctx else "http"
        url = "{}://127.0.0.1:{}".format(proto, port)
        return app, url

    yield create

    @asyncio.coroutine
    def finish():
        yield from app_handler.finish_connections()
        yield from app.finish()
        srv.close()
        yield from srv.wait_closed()

    loop.run_until_complete(finish())


@pytest.mark.tryfirst
def pytest_pycollect_makeitem(collector, name, obj):
    if collector.funcnamefilter(name):
        item = pytest.Function(name, parent=collector)
        if 'run_loop' in item.keywords:
            return list(collector._genfunctions(name, obj))


@pytest.mark.tryfirst
def pytest_pyfunc_call(pyfuncitem):
    """
    Run asyncio marked test functions in an event loop instead of a normal
    function call.
    """
    if 'run_loop' in pyfuncitem.keywords:
        funcargs = pyfuncitem.funcargs
        loop = funcargs['loop']
        testargs = {arg: funcargs[arg]
                    for arg in pyfuncitem._fixtureinfo.argnames}
        loop.run_until_complete(pyfuncitem.obj(**testargs))
        return True


def pytest_runtest_setup(item):
    if 'run_loop' in item.keywords and 'loop' not in item.fixturenames:
        # inject an event loop fixture for all async tests
        item.fixturenames.append('loop')
