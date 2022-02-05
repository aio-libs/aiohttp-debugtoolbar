import pytest
import jinja2
import aiohttp_jinja2
from aiohttp import web
from aiohttp_debugtoolbar import setup


@pytest.fixture
def create_server(aiohttp_unused_port):
    async def create(*, debug=False, ssl_ctx=None, **kw):
        app = web.Application()
        setup(app, **kw)

        tplt = """
        <html>
        <head></head>
        <body>
            <h1>{{ head }}</h1>{{ text }}
        </body>
        </html>"""
        loader = jinja2.DictLoader({"tplt.html": tplt})
        aiohttp_jinja2.setup(app, loader=loader)

        return app

    return create
