import pathlib

import aiohttp_jinja2

from aiohttp_debugtoolbar.panels.base import DebugPanel
from aiohttp_debugtoolbar.utils import TEMPLATE_KEY


async def test_request_vars_panel(create_server, aiohttp_client):
    async def handler(request):
        return aiohttp_jinja2.render_template(
            "tplt.html", request, {"head": "HEAD", "text": "text"}
        )

    app = await create_server()
    app.router.add_route("GET", "/", handler)
    # add cookie to request
    cookie = {"aiodtb_cookie": "aioDebugRequestPanel_Cookie"}
    client = await aiohttp_client(app, cookies=cookie)
    resp = await client.get("/")
    assert 200 == resp.status
    txt = await resp.text()
    # Toolbar Button exists on page
    assert "pDebugToolbarHandle" in txt

    # make sure that debug toolbar page working
    resp = await client.get("/_debugtoolbar")
    txt = await resp.text()
    assert "aioDebugRequestPanel_Cookie" in txt
    assert 200 == resp.status


async def test_extra_panel(create_server, aiohttp_client):
    async def handler(request):
        return aiohttp_jinja2.render_template(
            "tplt.html", request, {"head": "HEAD", "text": "text"}
        )

    class TestExtraPanel(DebugPanel):
        name = "aioTestExtraPanel"
        has_content = True
        template = "test.jinja2"
        title = name
        nav_title = title

        async def process_response(self, response):
            self.data = data = {}
            data.update(
                {
                    "panel_test": self.name,
                }
            )

    parent_path = pathlib.Path(__file__).parent
    app = await create_server(
        extra_panels=[TestExtraPanel], extra_templates=str(parent_path / "tpl")
    )
    app.router.add_route("GET", "/", handler)
    # make sure that toolbar button present on apps page
    client = await aiohttp_client(app)
    resp = await client.get("/")
    assert 200 == resp.status
    txt = await resp.text()
    assert "pDebugToolbarHandle" in txt

    # check template from extra_templates
    assert "test.jinja2" in app[TEMPLATE_KEY].list_templates()

    # make sure that debug toolbar page working and extra panel exists
    resp = await client.get("/_debugtoolbar")
    txt = await resp.text()
    assert 200 == resp.status
    assert "aioExtraPanelTemplate" in txt
    assert "aioTestExtraPanel" in txt
