import asyncio
import json
import logging
import os

import jinja2
import aiohttp_debugtoolbar
import aiohttp_jinja2
import aiohttp_mako
from aiohttp import web
from aiohttp_debugtoolbar import toolbar_middleware_factory


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__file__)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
templates = os.path.join(PROJECT_ROOT, 'templates')


def json_renderer(func):
    assert asyncio.iscoroutinefunction(func), func

    @asyncio.coroutine
    def wrapper(request):
        response = web.HTTPOk()
        context = yield from func(request)
        try:
            text = json.dumps(context)
        except TypeError:
            raise RuntimeError("{!r} result {!r} is not serializable".format(
                func, context))
        response.content_type = 'application/json'
        response.text = text
        return response

    return wrapper


@asyncio.coroutine
def exc(request):
    raise NotImplementedError


@aiohttp_mako.template('ajax.mako')
def test_ajax(request):
    return {'app': request.app}


@json_renderer
@asyncio.coroutine
def call_ajax(request):
    return {'ajax': 'success'}


@asyncio.coroutine
def test_redirect(request):
    raise web.HTTPSeeOther(location='/')


@aiohttp_mako.template('index.mako')
@asyncio.coroutine
def test_page(request):
    title = 'Aiohttp Debugtoolbar'

    return {
        'title': title,
        'show_jinja2_link': True,
        'show_sqla_link': False,
        'app': request.app}


@aiohttp_mako.template('error.mako')
def test_mako_exc(request):
    return {'title': 'Test mako template exceptions'}


@aiohttp_jinja2.template('error.jinja2')
def test_jinja2_exc(request):
    return {'title': 'Test jinja2 template exceptions'}


@asyncio.coroutine
def init(loop):
    app = web.Application(loop=loop, middlewares=[toolbar_middleware_factory])

    aiohttp_debugtoolbar.setup(app, intercept_exc='debug')

    aiohttp_mako.setup(app, input_encoding='utf-8',
                       output_encoding='utf-8',
                       default_filters=['decode.utf8'],
                       directories=[templates])

    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(templates))

    # static view
    app.router.add_static('/static', os.path.join(PROJECT_ROOT, 'static'))

    app.router.add_route('GET', '/redirect', test_redirect,
                         name='test_redirect')
    app.router.add_route('GET', '/', test_page, name='test_page')
    app.router.add_route('GET', '/exc', exc, name='test_exc')

    # ajax handlers
    app.router.add_route('GET', '/ajax', test_ajax, name='test_ajax')
    app.router.add_route('GET', '/call_ajax', call_ajax, name='call_ajax')

    # templates error handlers
    app.router.add_route('GET', '/mako_exc', test_mako_exc,
                         name='test_mako_exc')
    app.router.add_route('GET', '/jinja2_exc', test_jinja2_exc,
                         name='test_jinja2_exc')

    handler = app.make_handler()
    srv = yield from loop.create_server(handler, '127.0.0.1', 9000)
    log.debug("Server started at http://127.0.0.1:9000")
    return srv, handler


loop = asyncio.get_event_loop()
srv, handler = loop.run_until_complete(init(loop))
try:
    loop.run_forever()
except KeyboardInterrupt:
    loop.run_until_complete(handler.finish_connections())
