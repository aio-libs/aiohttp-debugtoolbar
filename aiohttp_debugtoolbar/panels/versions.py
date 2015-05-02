import sys
import platform
import pkg_resources
from operator import itemgetter

from .base import DebugPanel


__all__ = ['VersionDebugPanel']
_ = lambda x: x


packages = []
for distribution in pkg_resources.working_set:
    name = distribution.project_name
    deps = [d.project_name for d in distribution.requires()]
    packages.append({'version': distribution.version,
                     'lowername': name.lower(),
                     'name': name,
                     'dependencies': deps})

packages = sorted(packages, key=itemgetter('lowername'))
aiohttp_version = pkg_resources.get_distribution('aiohttp').version


class VersionDebugPanel(DebugPanel):
    """
    Panel that displays the Python version, the Pyramid version, and the
    versions of other software on your PYTHONPATH.
    """
    name = 'Version'
    has_content = True
    template = 'versions.dbtmako'
    title = _('Versions')
    nav_title = title

    def __init__(self, request):
        super().__init__(request)
        self.data = {'platform': self.get_platform(),
                     'packages': packages,
                     'aiohttp_version': aiohttp_version}

    def _get_platform_name(self):
        return platform.platform()

    def get_platform(self):
        return 'Python %s on %s' % (sys.version, self._get_platform_name())
