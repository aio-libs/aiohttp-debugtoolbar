import asyncio
import pytest
import aiohttp_jinja2
import pathlib
from aiohttp_debugtoolbar.panels.base import DebugPanel
from aiohttp import ClientSession


@pytest.mark.run_loop
def test_request_vars_panel(loop, create_server):
    @asyncio.coroutine
    def handler(request):
        return aiohttp_jinja2.render_template(
            'tplt.html', request,
            {'head': 'HEAD', 'text': 'text'})

    app, url = yield from create_server()
    app.router.add_route('GET', '/', handler)
    # add cookie to request
    cookie = {"aiodtb_cookie": "aioDebugRequestPanel_Cookie"}
    resp = yield from ClientSession(loop=loop, cookies=cookie).request(
        'GET', url + '/')
    assert 200 == resp.status
    txt = yield from resp.text()
    # Toolbar Button exists on page
    assert 'pDebugToolbarHandle' in txt

    # make sure that debug toolbar page working
    url = "{}/_debugtoolbar".format(url)
    resp = yield from ClientSession(loop=loop).request('GET', url)
    txt = yield from resp.text()
    assert 'aioDebugRequestPanel_Cookie' in txt
    assert 200 == resp.status


@pytest.mark.run_loop
def test_extra_panel(loop, create_server):
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
        _original_func = None

        def __init__(self, request):
            super().__init__(request)

        @asyncio.coroutine
        def process_response(self, response):
            self.data = data = {}
            data.update({
                'panel_test': self.name,
            })

    parent_path = pathlib.Path(__file__).parent
    app, url = yield from create_server(
        extra_panels=[TestExtraPanel],
        extra_templates=str(parent_path / 'tpl'))
    app.router.add_route('GET', '/', handler)
    # make sure that toolbar button present on apps page
    resp = yield from ClientSession(loop=loop).request('GET', url + '/')
    assert 200 == resp.status
    txt = yield from resp.text()
    assert 'pDebugToolbarHandle' in txt

    # check template from extra_templates
    assert 'test.jinja2' in app['aiohttp_debugtoolbar_jinja2'].list_templates()

    # make sure that debug toolbar page working and extra panel exists
    url = "{}/_debugtoolbar".format(url)
    resp = yield from ClientSession(loop=loop).request('GET', url)
    txt = yield from resp.text()
    assert 200 == resp.status
    assert 'aioExtraPanelTemplate' in txt
    assert 'aioTestExtraPanel' in txt
