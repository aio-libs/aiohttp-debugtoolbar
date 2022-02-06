import platform
import sys
from operator import itemgetter

import pkg_resources  # noqa: I900

from .base import DebugPanel

__all__ = ["VersionDebugPanel"]


packages = []
for distribution in pkg_resources.working_set:
    name = distribution.project_name
    dependencies = [d.project_name for d in distribution.requires()]

    # parse home page url
    metadata_file = distribution.PKG_INFO
    lines = distribution.get_metadata_lines(metadata_file)
    url = "#"
    for line in lines:
        if line.startswith("Home-page:"):
            url = line[10:].strip()
            break

    packages.append(
        {
            "version": distribution.version,
            "lowername": name.lower(),
            "name": name,
            "dependencies": dependencies,
            "url": url,
        }
    )

packages = sorted(packages, key=itemgetter("lowername"))
aiohttp_version = pkg_resources.get_distribution("aiohttp").version


class VersionDebugPanel(DebugPanel):
    """
    Panel that displays the Python version, the aiohttp version, and the
    versions of other software on your PYTHONPATH.
    """

    name = "Version"
    has_content = True
    template = "versions.jinja2"
    title = "Versions"
    nav_title = title

    def __init__(self, request):
        super().__init__(request)
        self.data = {
            "platform": self.get_platform(),
            "packages": packages,
            "aiohttp_version": aiohttp_version,
        }

    def _get_platform_name(self):
        return platform.platform()

    def get_platform(self):
        return f"Python {sys.version} on {self._get_platform_name()}"
