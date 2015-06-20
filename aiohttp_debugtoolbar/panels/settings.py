from operator import itemgetter

from .base import DebugPanel
from ..utils import APP_KEY


__all__ = ['SettingsDebugPanel']


class SettingsDebugPanel(DebugPanel):
    """
    A panel to display debug toolbar setting for now.
    """
    name = 'Settings'
    has_content = True
    template = 'settings.jinja2'
    title = 'Settings'
    nav_title = title

    def __init__(self, request):
        super().__init__(request)
        # TODO: show application setting here
        # always repr this stuff before it's sent to the template to appease
        # dumbass stuff like MongoDB's __getattr__ that always returns a
        # Collection, which fails when Jinja tries to look up __html__ on it.
        settings = request.app[APP_KEY]['settings']
        # filter out non-pyramid prefixed settings to avoid duplication
        reprs = [(k, repr(v)) for k, v in settings.items()]
        self.data = {'settings': sorted(reprs, key=itemgetter(0))}
