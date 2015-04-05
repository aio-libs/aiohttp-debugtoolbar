import os
import asyncio
import json
from aiohttp import web
import aiohttp_debugtoolbar
import aiohttp_mako
from aiohttp_debugtoolbar.middlewares import toolbar_middleware_factory

import logging
import sys

root = logging.getLogger()
root.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)


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


@asyncio.coroutine
def notfound(request):
    raise web.HTTPNotFound()


# @view_config(route_name='test_ajax', renderer='__main__:templates/ajax.mako')
@aiohttp_mako.template('ajax.mako')
def test_ajax(request):
    return {}


@json_renderer
@aiohttp_mako.template('ajax.mako')
def call_ajax(request):
    return {'ajax': 'success'}


@aiohttp_mako.template('notfound.mako')
def notfound_view(request):
    request.response.status_code = 404
    return aiohttp_mako.render_template('notfound.mako', request, {},
                                        status=404)


@asyncio.coroutine
def test_redirect(request):
    raise web.HTTPSeeOther(location='/')


@aiohttp_mako.template('index.mako')
@asyncio.coroutine
def test_page(request):
    title = 'Aiohttp Debugtoolbar'
    # log.info(title)

    return {
        'title': title,
        'show_jinja2_link': True,
        'show_sqla_link': False,
        'app': request.app}


@aiohttp_mako.template('error.mako')
@asyncio.coroutine
def test_template_exc(request):
    return {'title': 'Test template exceptions'}


here = os.path.dirname(os.path.abspath(__file__))
templates = os.path.join(here, 'templates')


@asyncio.coroutine
def init(loop):
    app = web.Application(loop=loop, middlewares=[toolbar_middleware_factory])

    aiohttp_debugtoolbar.setup(app)

    aiohttp_mako.setup(app, input_encoding='utf-8',
                       output_encoding='utf-8',
                       default_filters=['decode.utf8'],
                       directories=[templates],
    )

    app['DEBUG_TEMPLATE'] = True



    # static view
    app.router.add_static('/static', os.path.join(here, 'static'))
    # routes setup
    app.router.add_route('GET', '/redirect', test_redirect,
                         name='test_redirect')
    app.router.add_route('GET', '/', test_page, name='test_page')
    app.router.add_route('GET', '/exc', exc, name='test_exc')
    app.router.add_route('GET', '/notfound', notfound, name='test_notfound')
    app.router.add_route('GET', '/ajax', test_ajax, name='test_ajax')
    app.router.add_route('GET', '/call_ajax', call_ajax, name='call_ajax')
    app.router.add_route('GET', '/mako_exc', test_template_exc,
                         name='test_mako_exc')

    handler = app.make_handler()
    srv = yield from loop.create_server(handler, '127.0.0.1', 9000)
    print("Server started at http://127.0.0.1:9000")
    return srv, handler


loop = asyncio.get_event_loop()
srv, handler = loop.run_until_complete(init(loop))
try:
    loop.run_forever()
except KeyboardInterrupt:
    loop.run_until_complete(handler.finish_connections())
