import json
import sys

from aiohttp_debugtoolbar import APP_KEY


async def test_sse(create_server, aiohttp_client):
    async def handler(request):
        raise NotImplementedError

    app = await create_server()
    app.router.add_route("GET", "/", handler)
    client = await aiohttp_client(app)
    # make sure that exception page rendered
    resp = await client.get("/")
    txt = await resp.text()
    assert 500 == resp.status
    assert '<div class="debugger">' in txt

    # get request id from history
    history = app[APP_KEY]["request_history"]
    request_id = history[0][0]

    url = "/_debugtoolbar/sse"
    resp = await client.get(url)
    data = await resp.text()
    data = data.strip()

    # split and check EventSource data
    event_id, event, payload_raw = data.split("\n")
    assert event_id == f"id: {request_id}"
    assert event == "event: new_request"

    if sys.version_info >= (3, 9):
        payload_json = payload_raw.removeprefix("data: ")
    else:
        payload_json = payload_raw.strip("data: ")  # noqa: B005
    payload = json.loads(payload_json)
    expected = [
        [
            request_id,
            {"path": "/", "scheme": "http", "method": "GET", "status_code": 500},
            "",
        ]
    ]

    assert payload == expected, payload
