import asyncio
import aiohttp_jinja2
import pathlib
from aiohttp_debugtoolbar.panels.base import DebugPanel


@asyncio.coroutine
def test_request_vars_panel(create_server, test_client):
    @asyncio.coroutine
    def handler(request):
        return aiohttp_jinja2.render_template(
            'tplt.html', request,
            {'head': 'HEAD', 'text': 'text'})

    app = yield from create_server()
    app.router.add_route('GET', '/', handler)
    # add cookie to request
    cookie = {"aiodtb_cookie": "aioDebugRequestPanel_Cookie"}
    client = yield from test_client(app, cookies=cookie)
    resp = yield from client.get('/')
    assert 200 == resp.status
    txt = yield from resp.text()
    # Toolbar Button exists on page
    assert 'pDebugToolbarHandle' in txt

    # make sure that debug toolbar page working
    resp = yield from client.get('/_debugtoolbar')
    txt = yield from resp.text()
    assert 'aioDebugRequestPanel_Cookie' in txt
    assert 200 == resp.status


@asyncio.coroutine
def test_extra_panel(create_server, test_client):
    @asyncio.coroutine
    def handler(request):
        return aiohttp_jinja2.render_template(
            'tplt.html', request,
            {'head': 'HEAD', 'text': 'text'})

    class TestExtraPanel(DebugPanel):
        name = 'aioTestExtraPanel'
        has_content = True
        template = 'test.jinja2'
        title = name
        nav_title = title

        @asyncio.coroutine
        def process_response(self, response):
            self.data = data = {}
            data.update({
                'panel_test': self.name,
            })

    parent_path = pathlib.Path(__file__).parent
    app = yield from create_server(
        extra_panels=[TestExtraPanel],
        extra_templates=str(parent_path / 'tpl'))
    app.router.add_route('GET', '/', handler)
    # make sure that toolbar button present on apps page
    client = yield from test_client(app)
    resp = yield from client.get('/')
    assert 200 == resp.status
    txt = yield from resp.text()
    assert 'pDebugToolbarHandle' in txt

    # check template from extra_templates
    assert 'test.jinja2' in app['aiohttp_debugtoolbar_jinja2'].list_templates()

    # make sure that debug toolbar page working and extra panel exists
    resp = yield from client.get('/_debugtoolbar')
    txt = yield from resp.text()
    assert 200 == resp.status
    assert 'aioExtraPanelTemplate' in txt
    assert 'aioTestExtraPanel' in txt
