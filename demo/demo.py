import logging
from pathlib import Path

import aiohttp_jinja2
import jinja2
from aiohttp import web

import aiohttp_debugtoolbar

try:
    import aiohttp_mako
except ImportError:
    aiohttp_mako = None

PROJECT_ROOT = Path(__file__).parent
TEMPLATE_DIR = PROJECT_ROOT / 'templates'


@aiohttp_jinja2.template('index.jinja2')
async def index(request):
    log.info('Info logger fon index page')
    log.debug('Debug logger fon index page')
    log.critical('Critical logger fon index page')

    return {
        'title': 'Aiohttp Debugtoolbar',
        'aiohttp_mako': aiohttp_mako
    }


async def exception(request):
    log.error('NotImplementedError exception handler')
    raise NotImplementedError


@aiohttp_jinja2.template('ajax.jinja2')
async def ajax(request):
    if request.method == 'POST':
        log.info('Ajax POST request received')
        return web.json_response({'ajax': 'success'})


async def redirect(request):
    log.info('redirect handler')
    raise web.HTTPSeeOther(location='/')


@aiohttp_jinja2.template('error.jinja2')
async def jinja2_exception(request):
    return {'title': 'Test jinja2 template exceptions'}


@aiohttp_mako.template('error.mako')
async def mako_exception(request):
    return {'title': 'Test Mako template exceptions'}


async def init():
    PROJECT_ROOT = Path(__file__).parent

    app = web.Application()
    aiohttp_debugtoolbar.setup(app, intercept_exc='debug')

    loader = jinja2.FileSystemLoader([str(TEMPLATE_DIR)])
    aiohttp_jinja2.setup(app, loader=loader)

    routes = [
        web.get('/', index, name='index'),
        web.get('/redirect', redirect, name='redirect'),
        web.get('/exception', exception, name='exception'),
        web.get('/jinja2_exc', jinja2_exception, name='jinja2_exception'),
        web.get('/ajax', ajax, name='ajax'),
        web.post('/ajax', ajax, name='ajax'),
        web.static('/static', PROJECT_ROOT / 'static'),
    ]

    if aiohttp_mako:
        mako_cfg = {
            'input_encoding': 'utf-8',
            'output_encoding': 'utf-8',
            'default_filters': ['decode.utf8'],
            'directories': [str(TEMPLATE_DIR)],
        }
        aiohttp_mako.setup(app, **mako_cfg)
        route = web.get('/mako_exc', mako_exception, name='mako_exception')
        routes.append(route)

    app.add_routes(routes)
    return app


if __name__ == '__main__':
    log = logging.getLogger(__file__)
    logging.basicConfig(level=logging.DEBUG)

    web.run_app(init(), host='127.0.0.1', port=9000)
