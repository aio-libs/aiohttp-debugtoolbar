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
def mako_exception(request):
    return {'title': 'Test Mako template exceptions'}


def main():

    app = web.Application()
    aiohttp_debugtoolbar.setup(app, intercept_exc='debug')

    loader = jinja2.FileSystemLoader([str(TEMPLATE_DIR)])
    aiohttp_jinja2.setup(app, loader=loader)

    app.router.add_get('/', index, name='index')
    app.router.add_get('/ajax', ajax, name='ajax')
    app.router.add_post('/ajax', ajax, name='ajax')
    app.router.add_get('/redirect', redirect, name='redirect')
    app.router.add_get('/exception', exception, name='exception')
    app.router.add_get('/jinja2_exc', jinja2_exception, name='jinja2_exception')
    app.router.add_static('/static', PROJECT_ROOT / 'static')

    if aiohttp_mako:
        aiohttp_mako.setup(app, input_encoding='utf-8',
                           output_encoding='utf-8',
                           default_filters=['decode.utf8'],
                           directories=[str(TEMPLATE_DIR)])

        app.router.add_get('/mako_exc', mako_exception, name='mako_exception')

    web.run_app(app, host='127.0.0.1', port=9000)


if __name__ == '__main__':

    log = logging.getLogger(__file__)
    logging.basicConfig(level=logging.DEBUG)

    main()
