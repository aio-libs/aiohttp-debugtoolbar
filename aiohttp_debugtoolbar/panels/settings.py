from operator import itemgetter

from .base import DebugPanel
from ..utils import APP_KEY


__all__ = ['SettingsDebugPanel']
_ = lambda x: x


class SettingsDebugPanel(DebugPanel):
    """
    A panel to display Pyramid deployment settings for your application (the
    values in ``registry.settings``).
    """
    name = 'Settings'
    has_content = True
    template = 'settings.dbtmako'
    title = _('Settings')
    nav_title = title

    def __init__(self, request):
        super().__init__(request)

        # always repr this stuff before it's sent to the template to appease
        # dumbass stuff like MongoDB's __getattr__ that always returns a
        # Collection, which fails when Jinja tries to look up __html__ on it.
        settings = request.app[APP_KEY]['settings']
        # filter out non-pyramid prefixed settings to avoid duplication
        reprs = [(k, repr(v)) for k, v in settings.items()]
        self.data = {'settings': sorted(reprs, key=itemgetter(0))}
