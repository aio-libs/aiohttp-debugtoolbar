import inspect

from .base import DebugPanel


__all__ = ['RoutesDebugPanel']


class RoutesDebugPanel(DebugPanel):
    """
    A panel to display the routes used by your aiohttp application.
    """
    name = 'Routes'
    has_content = True
    template = 'routes.jinja2'
    title = 'Routes'
    nav_title = title

    def __init__(self, request):
        super().__init__(request)
        self.populate(request)

    def populate(self, request):
        info = []
        router = request.app.router

        for route in router.routes():
            info.append({
                "name": route.name or '',
                "method": route.method,
                "info": sorted(route.get_info().items()),
                "handler": repr(route.handler),
                "source": inspect.getsource(route.handler)
            })

        self.data = {'routes': info}
