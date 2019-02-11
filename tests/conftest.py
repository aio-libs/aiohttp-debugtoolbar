import sys
from pathlib import Path

import aiohttp_jinja2
import jinja2
import pytest
from aiohttp import web

from aiohttp_debugtoolbar import setup


DEFAULT_TEMPLATE_DIR = Path(__file__).parent / 'templates'


def pytest_ignore_collect(path, config):
    if 'pep492' in str(path):
        if sys.version_info < (3, 5, 0):
            return True


@pytest.fixture
def create_server(aiohttp_unused_port):

    def create(**kwargs):
        app = web.Application()
        setup(app, **kwargs)
        loader = jinja2.FileSystemLoader(str(DEFAULT_TEMPLATE_DIR))
        aiohttp_jinja2.setup(app, loader=loader)
        return app

    return create
