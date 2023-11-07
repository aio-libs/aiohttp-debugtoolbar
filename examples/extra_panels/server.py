import pathlib
import sys

import aiohttp_jinja2
import jinja2
from aiohttp import web

import aiohttp_debugtoolbar

try:
    import aiopg
    from extra_pgsql import RequestPgDebugPanel
except ImportError:
    print("Module aiopg not installed")

try:
    import aioredis
    from extra_redis import RequestRedisDebugPanel
except ImportError:
    print("Module aioredis not installed")

PATH_PARENT = pathlib.Path(__file__).parent

db_key = web.AppKey["aiopg.Pool"]("db_key")
redis_key = web.AppKey["aioredis.Redis"]("redis_key")


@aiohttp_jinja2.template("index.html")
async def basic_handler(request):
    # testing for PgSQL
    if "db" in request.app:
        conn = await request.app[db_key].acquire()
        cur = await conn.cursor()

        await cur.execute("SELECT 1")
        ret = []
        for row in cur:
            ret.append(row)
        assert ret == [(1,)]  # noqa: S101

        await request.app[db_key].release(conn)

    # testing for Redis
    if "redis" in request.app:
        with (await request.app[redis_key]) as redis:
            await redis.set("TEST", "VAR", expire=5)
            assert b"VAR" == (await redis.get("TEST"))  # noqa: S101

    return {
        "title": "example aiohttp_debugtoolbar!",
        "text": "Hello aiohttp_debugtoolbar!",
        "app": request.app,
    }


async def exception_handler(request):
    raise NotImplementedError


async def close_pg(app):
    app[db_key].close()
    await app[db_key].wait_closed()


async def close_redis(app):
    app[redis_key].close()
    await app[redis_key].wait_closed()


async def init():
    # add aiohttp_debugtoolbar middleware to you application
    app = web.Application()

    extra_panels = []
    if "aiopg" in sys.modules:
        extra_panels.append(RequestPgDebugPanel)
    if "aioredis" in sys.modules:
        extra_panels.append(RequestRedisDebugPanel)

    # install aiohttp_debugtoolbar
    aiohttp_debugtoolbar.setup(
        app, extra_panels=extra_panels, extra_templates=str(PATH_PARENT / "extra_tpl")
    )

    template = """
    <html>
        <head>
            <title>{{ title }}</title>
        </head>
        <body>
            <h1>{{ text }}</h1>
            <p>
              <a href="{{ app.router['exc_example'].url_for() }}">
              Exception example</a>
            </p>
        </body>
    </html>
    """
    # install jinja2 templates
    loader = jinja2.DictLoader({"index.html": template})
    aiohttp_jinja2.setup(app, loader=loader)

    # init routes for index page, and page with error
    app.router.add_route("GET", "/", basic_handler, name="index")
    app.router.add_route("GET", "/exc", exception_handler, name="exc_example")

    if "aiopg" in sys.modules:
        # create connection to the database
        dsn = "host={host} dbname={db} user={user} password={passw} ".format(
            db="postgres", user="developer", passw="1", host="localhost"
        )
        app[db_key] = await aiopg.create_pool(dsn, minsize=1, maxsize=2)
        # Correct PostgreSQL shutdown
        app.on_cleanup.append(close_pg)

    if "aioredis" in sys.modules:
        # create redis pool
        app[redis_key] = await aioredis.Redis("127.0.0.1", 6379)
        # Correct Redis shutdown
        app.on_cleanup.append(close_redis)

    return app


web.run_app(init(), host="127.0.0.1", port=9000)
