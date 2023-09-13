import sys
from unittest.mock import create_autospec

import pytest
from aiohttp import web

from aiohttp_debugtoolbar.panels import VersionDebugPanel


@pytest.mark.skipif(sys.version_info < (3, 8), reason="Missing importlib.metadata")
async def test_packages():
    request_mock = create_autospec(web.Request)
    panel = VersionDebugPanel(request_mock)

    jinja2_metadata = next(p for p in panel.data["packages"] if p["name"] == "Jinja2")
    assert "version" in jinja2_metadata
    assert jinja2_metadata["lowercase"] == "jinja2"
    assert any("MarkupSafe" in d for d in jinja2_metadata["dependencies"])
    assert "url" in jinja2_metadata
