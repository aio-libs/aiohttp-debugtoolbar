import sys
from unittest.mock import create_autospec

import pytest
from aiohttp import web
from aiohttp_debugtoolbar.panels import VersionDebugPanel


@pytest.mark.skipif(sys.version_info < (3, 8), reason="Missing importlib.metadata")
async def test_packages():
    request_mock = create_autospec(web.Request)
    panel = VersionDebugPanel(request_mock)

    jinja2_metadata = {
        "version": "3.0.3",
        "lowername": "jinja2",
        "name": "Jinja2",
        "dependencies": ["MarkupSafe (>=2.0)", "Babel (>=2.7) ; extra == 'i18n'"],
        "url": "https://palletsprojects.com/p/jinja/",
    }
    assert jinja2_metadata in panel.data["packages"]
