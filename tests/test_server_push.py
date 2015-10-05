import asyncio
import json
import aiohttp

from aiohttp_debugtoolbar import APP_KEY


def test_sse(loop, create_server):
    @asyncio.coroutine
    def handler(request):
        raise NotImplementedError

    @asyncio.coroutine
    def go():
        app, url = yield from create_server()
        app.router.add_route('GET', '/', handler)
        # make sure that exception page rendered
        resp = yield from aiohttp.request('GET', url, loop=loop)
        txt = yield from resp.text()
        assert 500 == resp.status
        assert '<div class="debugger">' in txt

        # get request id from history
        history = app[APP_KEY]['request_history']
        request_id = history[0][0]

        url = '{}/_debugtoolbar/sse'.format(url)
        resp = yield from aiohttp.request('GET', url, loop=loop)
        data = yield from resp.text()
        data = data.strip()

        # split and check EventSource data
        event_id, event, payload_raw = data.split('\n')
        assert event_id == 'id: {}'.format(request_id)
        assert event == 'event: new_request'

        payload_json = payload_raw.strip('data: ')
        payload = json.loads(payload_json)
        expected = [[request_id, {"path": "/",
                                  "scheme": "http",
                                  "method": "GET",
                                  "status_code": 500},
                     ""]]

        assert payload == expected, payload

    loop.run_until_complete(go())
