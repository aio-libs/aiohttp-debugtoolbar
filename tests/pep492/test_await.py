import aiohttp
import aiohttp_jinja2
import jinja2
from aiohttp import web
from aiohttp_debugtoolbar import middleware, setup as tbsetup


def test_handler_is_native_coroutine(loop, create_server):
    async def handler(request):
        resp = web.Response(body=b'native coroutine', status=200,
                            content_type='text/plain')
        return resp

    async def go():
        app, url = await create_server()
        app.router.add_route('GET', '/', handler)
        resp = await aiohttp.request('GET', url+'/', loop=loop)
        assert 200 == resp.status

        body = await resp.read()
        assert b'native coroutine' == body
