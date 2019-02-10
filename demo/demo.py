import logging
import sys

from pathlib import Path

import jinja2
import aiohttp_debugtoolbar
import aiohttp_jinja2
from aiohttp import web

try:
    import aiohttp_mako
except ImportError:
    aiohttp_mako = None


parent = Path('.').parent
parent = str(parent.absolute())
sys.path.insert(0, parent)

log = logging.getLogger(__file__)


async def exc(request):
    log.error('NotImplementedError exception handler')
    raise NotImplementedError


@aiohttp_jinja2.template('ajax.jinja2')
async def test_ajax(request):
    return {'ajax_url': request.app.router['call_ajax'].url_for()}


async def call_ajax(request):
    log.info('call_ajax handler')
    return web.json_response({'ajax': 'success'})


async def test_redirect(request):
    log.info('redirect handler')
    raise web.HTTPSeeOther(location='/')


@aiohttp_jinja2.template('index.jinja2')
async def test_page(request):
    title = 'Aiohttp Debugtoolbar'

    log.info('Info logger fon index page')
    log.debug('Debug logger fon index page')
    log.critical('Critical logger fon index page')

    return {
        'title': title,
        'show_jinja2_link': True,
        'show_sqla_link': False,
        'app': request.app,
        'aiohttp_mako': aiohttp_mako}


@aiohttp_jinja2.template('error.jinja2')
async def test_jinja2_exc(request):
    return {'title': 'Test jinja2 template exceptions'}


def main():
    logging.basicConfig(level=logging.DEBUG)
    PROJECT_ROOT = Path(__file__).parent
    templates = PROJECT_ROOT / 'templates'

    app = web.Application()

    aiohttp_debugtoolbar.setup(app, intercept_exc='debug')
    loader = jinja2.FileSystemLoader([str(templates)])
    aiohttp_jinja2.setup(app, loader=loader)

    if aiohttp_mako:
        aiohttp_mako.setup(app, input_encoding='utf-8',
                           output_encoding='utf-8',
                           default_filters=['decode.utf8'],
                           directories=[str(templates)])

        @aiohttp_mako.template('error.mako')
        def test_mako_exc(request):
            return {'title': 'Test Mako template exceptions'}

        app.router.add_route('GET', '/mako_exc', test_mako_exc,
                             name='test_mako_exc')

    # static view
    app.router.add_static('/static', PROJECT_ROOT / 'static')

    app.router.add_route('GET', '/redirect', test_redirect,
                         name='test_redirect')
    app.router.add_route('GET', '/', test_page, name='test_page')
    app.router.add_route('GET', '/exc', exc, name='test_exc')

    # ajax handlers
    app.router.add_route('GET', '/ajax', test_ajax, name='test_ajax')
    app.router.add_route('GET', '/call_ajax', call_ajax, name='call_ajax')

    # templates error handlers
    app.router.add_route('GET', '/jinja2_exc', test_jinja2_exc,
                         name='test_jinja2_exc')

    web.run_app(app, host='127.0.0.1', port=9000)


if __name__ == '__main__':

    main()
