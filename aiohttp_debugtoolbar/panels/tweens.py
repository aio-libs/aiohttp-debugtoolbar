from aiohttp_debugtoolbar.utils import STATIC_ROUTE_NAME
from .base import DebugPanel

__all__ = ['MiddlewaresDebugPanel']
_ = lambda x: x


class MiddlewaresDebugPanel(DebugPanel):
    """
    A panel to display the tweens used by your Pyramid application.
    """
    name = 'Tweens'
    has_content = True
    template = 'tweens.dbtmako'
    title = _('Tweens')
    nav_title = title

    def __init__(self, request):
        super().__init__(request)
        if not request.app.middlewares:
            self.has_content = False
            self.is_active = False
        else:
            self.populate(request)

    def populate(self, request):
        # TODO: fix this works only for functions and classes
        tweens = [t.__name__ for t in request.app.middlewares]
        self.data = {'tweens': tweens}

    def render_vars(self, request):
        static_path = self._request.app.router[STATIC_ROUTE_NAME]\
            .url(filename='')
        return {'static_path': static_path}
