import asyncio
import jinja2
import aiohttp_debugtoolbar
import aiohttp_jinja2
import pathlib

from aiohttp import web

# extra panels
import sys

try:
    import aiopg
    from extra_pgsql import RequestPgDebugPanel
except ImportError:
    print("Module aiopg not installed")

try:
    from aioredis import create_pool
    from extra_redis import RequestRedisDebugPanel
except ImportError:
    print("Module aioredis not installed")

PATH_PARENT = pathlib.Path(__file__).parent


@aiohttp_jinja2.template('index.html')
async def basic_handler(request):
    # testing for PgSQL
    if 'db' in request.app:
        conn = await request.app['db'].acquire()
        cur = await conn.cursor()

        await cur.execute("SELECT 1")
        ret = []
        for row in cur:
            ret.append(row)
        assert ret == [(1,)]

        await request.app['db'].release(conn)

    # testing for Redis
    if 'redis' in request.app:
        with (await request.app['redis']) as redis:
            await redis.set('TEST', 'VAR', expire=5)
            assert b'VAR' == (await redis.get('TEST'))

    return {'title': 'example aiohttp_debugtoolbar!',
            'text': 'Hello aiohttp_debugtoolbar!',
            'app': request.app}


async def exception_handler(request):
    raise NotImplementedError


async def close_pg(app):
    app['db'].close()
    await app['db'].wait_closed()


async def close_redis(app):
    app['redis'].close()
    await app['redis'].wait_closed()


async def init(loop):
    # add aiohttp_debugtoolbar middleware to you application
    app = web.Application(loop=loop)

    extra_panels = []
    if 'aiopg' in sys.modules:
        extra_panels.append(RequestPgDebugPanel)
    if 'aioredis' in sys.modules:
        extra_panels.append(RequestRedisDebugPanel)

    # install aiohttp_debugtoolbar
    aiohttp_debugtoolbar.setup(
        app,
        extra_panels=extra_panels,
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

    if 'aiopg' in sys.modules:
        # create connection to the database
        dsn = 'host={host} dbname={db} user={user} password={passw} '.format(
            db='postgres', user='developer', passw='1', host='localhost')
        app['db'] = await aiopg.create_pool(
            dsn, loop=loop, minsize=1, maxsize=2)
        # Correct PostgreSQL shutdown
        app.on_cleanup.append(close_pg)

    if 'aioredis' in sys.modules:
        # create redis pool
        app['redis'] = await create_pool(('127.0.0.1', '6379'))
        # Correct Redis shutdown
        app.on_cleanup.append(close_redis)

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
