from aiohttp_debugtoolbar import APP_KEY


async def test_view_source(create_server, test_client):
    async def handler(request):
        raise NotImplementedError

    app = await create_server()
    app.router.add_route('GET', '/', handler)
    client = await test_client(app)

    # make sure that exception page rendered
    resp = await client.get('/')
    txt = await resp.text()
    assert 500 == resp.status
    assert '<div class="debugger">' in txt

    token = app[APP_KEY]['pdtb_token']
    exc_history = app[APP_KEY]['exc_history']

    for frame_id in exc_history.frames:
        source_url = '/_debugtoolbar/source?frm={}&token={}'.format(
            frame_id, token)
        exc_history = app[APP_KEY]['exc_history']
        resp = await client.get(source_url)
        await resp.text()
        assert resp.status == 200


async def test_view_execute(create_server, test_client):
    async def handler(request):
        raise NotImplementedError

    app = await create_server()
    app.router.add_route('GET', '/', handler)
    client = await test_client(app)
    # make sure that exception page rendered
    resp = await client.get('/')
    txt = await resp.text()
    assert 500 == resp.status
    assert '<div class="debugger">' in txt

    token = app[APP_KEY]['pdtb_token']
    exc_history = app[APP_KEY]['exc_history']

    source_url = '/_debugtoolbar/source'
    execute_url = '/_debugtoolbar/execute'
    for frame_id in exc_history.frames:
        params = {'frm': frame_id, 'token': token}
        resp = await client.get(source_url, params=params)
        await resp.text()
        assert resp.status == 200

        params = {'frm': frame_id, 'token': token,
                  'cmd': 'dump(object)'}
        resp = await client.get(execute_url, params=params)
        await resp.text()
        assert resp.status == 200

    # wrong token
    params = {'frm': frame_id, 'token': 'x', 'cmd': 'dump(object)'}
    resp = await client.get(execute_url, params=params)
    assert resp.status == 400
    # no token at all
    params = {'frm': frame_id, 'cmd': 'dump(object)'}
    resp = await client.get(execute_url, params=params)
    assert resp.status == 400


async def test_view_exception(create_server, test_client):
    async def handler(request):
        raise NotImplementedError

    app = await create_server()
    app.router.add_route('GET', '/', handler)
    client = await test_client(app)
    # make sure that exception page rendered
    resp = await client.get('/')
    txt = await resp.text()
    assert 500 == resp.status
    assert '<div class="debugger">' in txt

    token = app[APP_KEY]['pdtb_token']
    exc_history = app[APP_KEY]['exc_history']

    tb_id = list(exc_history.tracebacks.keys())[0]
    url = '/_debugtoolbar/exception?tb={}&token={}'.format(
        tb_id, token)

    resp = await client.get(url)
    await resp.text()
    assert resp.status == 200
    assert '<div class="debugger">' in txt
