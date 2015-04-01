import sys
import platform
import pkg_resources
from operator import itemgetter

from .base import DebugPanel

_ = lambda x: x

packages = []
for distribution in pkg_resources.working_set:
    name = distribution.project_name
    packages.append({'version': distribution.version,
                     'lowername': name.lower(),
                     'name': name})

packages = sorted(packages, key=itemgetter('lowername'))
pyramid_version = pkg_resources.get_distribution('pyramid').version


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
        self._data = {'platform': self.get_platform(), 'packages': packages}

    def _get_platform_name(self):
        return platform.platform()

    def get_platform(self):
        return 'Python %s on %s' % (sys.version, self._get_platform_name())
