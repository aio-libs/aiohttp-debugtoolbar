import asyncio
import sys

import pytest
import jinja2
import aiohttp_jinja2
from aiohttp import web
from aiohttp_debugtoolbar import setup


def pytest_ignore_collect(path, config):
    if 'pep492' in str(path):
        if sys.version_info < (3, 5, 0):
            return True


@pytest.fixture
def create_server(aiohttp_unused_port):

    @asyncio.coroutine
    def create(*, debug=False, ssl_ctx=None, **kw):
        app = web.Application()
        setup(app, **kw)

        tplt = """
        <html>
        <head></head>
        <body>
            <h1>{{ head }}</h1>{{ text }}
        </body>
        </html>"""
        loader = jinja2.DictLoader({'tplt.html': tplt})
        aiohttp_jinja2.setup(app, loader=loader)

        return app

    return create
