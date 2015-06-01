from aiohttp.web_urldispatcher import PlainRoute, DynamicRoute, StaticRoute
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

        for route in router._urls:
            pattern = None
            if isinstance(route, PlainRoute):
                pattern = route._path
            elif isinstance(route, DynamicRoute):
                pattern = route._formatter
            elif isinstance(route, StaticRoute):
                pattern = route._prefix

            info.append({
                "name": route.name,
                "method": route.method,
                "pattern": pattern,
                "handler": repr(route.handler)
            })

        self.data = {'routes': info}
