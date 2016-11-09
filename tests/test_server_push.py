import asyncio
import json

from aiohttp_debugtoolbar import APP_KEY


@asyncio.coroutine
def test_sse(create_server, test_client):
    @asyncio.coroutine
    def handler(request):
        raise NotImplementedError

    app = yield from create_server()
    app.router.add_route('GET', '/', handler)
    client = yield from test_client(app)
    # make sure that exception page rendered
    resp = yield from client.get('/')
    txt = yield from resp.text()
    assert 500 == resp.status
    assert '<div class="debugger">' in txt

    # get request id from history
    history = app[APP_KEY]['request_history']
    request_id = history[0][0]

    url = '/_debugtoolbar/sse'
    resp = yield from client.get(url)
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
