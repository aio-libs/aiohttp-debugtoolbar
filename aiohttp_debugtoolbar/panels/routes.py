from .base import DebugPanel


_ = lambda x: x

raise NotImplementedError

IRoutesMapper = None
IRouteRequest = None
Interface = None
IViewClassifier = None
IView = None


class RoutesDebugPanel(DebugPanel):
    """
    A panel to display the routes used by your Pyramid application.
    """
    name = 'Routes'
    has_content = True
    template = 'routes.dbtmako'
    title = _('Routes')
    nav_title = title

    def __init__(self, request):
        self.mapper = request.registry.queryUtility(IRoutesMapper)
        if self.mapper is None:
            self.has_content = False
            self.is_active = False
        else:
            self.populate(request)

    def populate(self, request):
        info = []
        mapper = self.mapper
        if mapper is not None:
            registry = request.registry
            routeinfo = getattr(registry, 'debugtoolbar_routeinfo', None)
            if routeinfo is None:
                routes = mapper.get_routes()
                for route in routes:
                    request_iface = registry.queryUtility(IRouteRequest,
                                                          name=route.name)
                    view_callable = None
                    if (request_iface is None) or (route.factory is not None):
                        view_callable = '<unknown>'
                    else:
                        view_callable = registry.adapters.lookup(
                            (IViewClassifier, request_iface, Interface),
                            IView, name='', default=None)
                    predicates = []
                    for predicate in route.predicates:
                        text = getattr(predicate, '__text__', repr(predicate))
                        predicates.append(text)
                    info.append({'route': route,
                                 'view_callable': view_callable,
                                 'predicates': ', '.join(predicates)})
                registry.debugtoolbar_routeinfo = info

            self.data = {
                'routes': registry.debugtoolbar_routeinfo,
            }
