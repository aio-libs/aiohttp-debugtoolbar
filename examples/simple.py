import asyncio

import aiohttp_jinja2
import jinja2
from aiohttp import web

import aiohttp_debugtoolbar


@aiohttp_jinja2.template('index.html')
def basic_handler(request):
    return {'title': 'example aiohttp_debugtoolbar!',
            'text': 'Hello aiohttp_debugtoolbar!',
            'app': request.app}


async def exception_handler(request):
    raise NotImplementedError


async def init(loop):
    # add aiohttp_debugtoolbar middleware to you application
    app = web.Application(loop=loop)
    # install aiohttp_debugtoolbar
    aiohttp_debugtoolbar.setup(app)

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
    srv = await loop.create_server(handler, '127.0.0.1', 9000)
    print("Server started at http://127.0.0.1:9000")
    return srv, handler


loop = asyncio.get_event_loop()
srv, handler = loop.run_until_complete(init(loop))
try:
    loop.run_forever()
except KeyboardInterrupt:
    loop.run_until_complete(handler.finish_connections())
