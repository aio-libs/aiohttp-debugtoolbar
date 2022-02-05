from aiohttp import web


async def test_handler_is_native_coroutine(create_server, aiohttp_client):
    async def handler(request):
        resp = web.Response(
            body=b"native coroutine", status=200, content_type="text/plain"
        )
        return resp

    app = await create_server()
    app.router.add_route("GET", "/", handler)
    client = await aiohttp_client(app)
    resp = await client.get("/")
    assert 200 == resp.status

    body = await resp.read()
    assert b"native coroutine" == body
