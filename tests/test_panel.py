import aiohttp_jinja2
import pathlib
from aiohttp_debugtoolbar.panels.base import DebugPanel


async def test_request_vars_panel(create_server, aiohttp_client):
    @aiohttp_jinja2.template('default.jinja2')
    async def handler(request):
        return {'head': 'HEAD', 'text': 'text'}

    app = create_server()
    app.router.add_route('GET', '/', handler)
    # add cookie to request
    cookie = {"aiodtb_cookie": "aioDebugRequestPanel_Cookie"}
    client = await aiohttp_client(app, cookies=cookie)
    resp = await client.get('/')
    assert 200 == resp.status
    txt = await resp.text()
    # Toolbar Button exists on page
    assert 'pDebugToolbarHandle' in txt

    # make sure that debug toolbar page working
    resp = await client.get('/_debugtoolbar')
    txt = await resp.text()
    assert 'aioDebugRequestPanel_Cookie' in txt
    assert 200 == resp.status


async def test_extra_panel(create_server, aiohttp_client):
    @aiohttp_jinja2.template('default.jinja2')
    async def handler(request):
        return {'head': 'HEAD', 'text': 'text'}

    class TestExtraPanel(DebugPanel):
        name = 'aioTestExtraPanel'
        has_content = True
        template = 'extra_panel.jinja2'
        title = name
        nav_title = title

        async def process_response(self, response):
            self.data = data = {}
            data.update({
                'panel_test': self.name,
            })

    parent_path = pathlib.Path(__file__).parent
    app = create_server(
        extra_panels=[TestExtraPanel],
        extra_templates=str(parent_path / 'extra_templates'))
    app.router.add_route('GET', '/', handler)
    # make sure that toolbar button present on apps page
    client = await aiohttp_client(app)
    resp = await client.get('/')
    assert 200 == resp.status
    txt = await resp.text()
    assert 'pDebugToolbarHandle' in txt

    # check template from extra_templates
    assert 'extra_panel.jinja2' in app['aiohttp_debugtoolbar_jinja2'].list_templates()

    # make sure that debug toolbar page working and extra panel exists
    resp = await client.get('/_debugtoolbar')
    txt = await resp.text()
    assert 200 == resp.status
    assert 'aioExtraPanelTemplate' in txt
    assert 'aioTestExtraPanel' in txt
