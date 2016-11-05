import asyncio
import jinja2
import aiohttp_debugtoolbar
import aiohttp_jinja2
import pathlib

from aiohttp import web
from .extra_pgsql import RequestPgDebugPanel
from .extra_redis import RequestRedisDebugPanel

PATH_PARENT = pathlib.Path(__file__).parent


@aiohttp_jinja2.template('index.html')
def basic_handler(request):
    # TODO: add testing for PgSQL
    # TODO: add testing for Redis
    return {'title': 'example aiohttp_debugtoolbar!',
            'text': 'Hello aiohttp_debugtoolbar!',
            'app': request.app}


@asyncio.coroutine
def exception_handler(request):
    raise NotImplementedError


@asyncio.coroutine
def init(loop):
    # add aiohttp_debugtoolbar middleware to you application
    app = web.Application(loop=loop)
    # install aiohttp_debugtoolbar
    aiohttp_debugtoolbar.setup(
        app,
        extra_panels=[RequestPgDebugPanel, RequestRedisDebugPanel],
        extra_templates=str(PATH_PARENT / 'extra_tpl'))

    template = """
    <html>
        <head>
            <title>{{ title }}</title>
        </head>
        <body>
            <h1>{{ text }}</h1>
            <p>
              <a href="{{ app.router['exc_example'].url() }}">
              Exception example</a>
            </p>
        </body>
    </html>
    """
    # install jinja2 templates
    loader = jinja2.DictLoader({'index.html': template})
    aiohttp_jinja2.setup(app, loader=loader)

    # init routes for index page, and page with error
    app.router.add_route('GET', '/', basic_handler, name='index')
    app.router.add_route('GET', '/exc', exception_handler, name='exc_example')

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
