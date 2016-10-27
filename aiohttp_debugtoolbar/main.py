import os
from pathlib import Path
import jinja2
import aiohttp_jinja2

from . import views
from . import panels
from .middlewares import middleware
from .utils import APP_KEY, TEMPLATE_KEY, STATIC_ROUTE_NAME, hexlify, \
    ToolbarStorage, ExceptionHistory
from .views import ExceptionDebugView

default_panel_names = [
    panels.HeaderDebugPanel,
    panels.PerformanceDebugPanel,
    panels.RequestVarsDebugPanel,
    panels.TracebackPanel,
    panels.LoggingPanel,
]


default_global_panel_names = [
    panels.RoutesDebugPanel,
    panels.SettingsDebugPanel,
    panels.MiddlewaresDebugPanel,
    panels.VersionDebugPanel,
]


default_settings = {
    'enabled': True,
    'intercept_exc': 'debug',  # display or debug or False
    'intercept_redirects': True,
    'panels': default_panel_names,
    'extra_panels': [],
    'global_panels': default_global_panel_names,
    'extra_global_panels': [],
    'hosts': ['127.0.0.1', '::1'],
    'exclude_prefixes': [],
    'button_style': '',
    'max_request_history': 100,
    'max_visible_requests': 10,
    'path_prefix': '/_debugtoolbar',
}


def setup(app, **kw):
    config = {}
    config.update(default_settings)
    config.update(kw)

    APP_ROOT = Path(__file__).parent
    app[APP_KEY] = {}
    if middleware not in app.middlewares:
        app.middlewares.append(middleware)

    templates_app = APP_ROOT / 'templates'
    templates_panels = APP_ROOT / 'panels/templates'

    app[APP_KEY]['settings'] = config
    loader = jinja2.FileSystemLoader([str(templates_app),
                                      str(templates_panels)])
    aiohttp_jinja2.setup(app, loader=loader, app_key=TEMPLATE_KEY)

    static_location = APP_ROOT / 'static'

    exc_handlers = ExceptionDebugView()

    path_prefix = config['path_prefix']
    app.router.add_static(path_prefix + '/static', static_location,
                          name=STATIC_ROUTE_NAME)

    app.router.add_route('GET', path_prefix + '/source', exc_handlers.source,
                         name='debugtoolbar.source')
    app.router.add_route('GET', path_prefix + '/execute', exc_handlers.execute,
                         name='debugtoolbar.execute')
    # app.router.add_route('GET', path_prefix + '/console',
    # exc_handlers.console,
    #                      name='debugtoolbar.console')
    app.router.add_route('GET', path_prefix + '/exception',
                         exc_handlers.exception,
                         name='debugtoolbar.exception')
    # TODO: fix when sql will be ported
    # app.router.add_route('GET', path_prefix + '/sqlalchemy/sql_select',
    #                      name='debugtoolbar.sql_select')
    # app.router.add_route('GET', path_prefix + '/sqlalchemy/sql_explain',
    #                      name='debugtoolbar.sql_explain')

    app.router.add_route('GET', path_prefix + '/sse', views.sse,
                         name='debugtoolbar.sse')

    app.router.add_route('GET', path_prefix + '/{request_id}',
                         views.request_view, name='debugtoolbar.request')
    app.router.add_route('GET', path_prefix, views.request_view,
                         name='debugtoolbar.main')

    def settings_opt(name):
        return app[APP_KEY]['settings'][name]

    max_request_history = settings_opt('max_request_history')

    app[APP_KEY]['request_history'] = ToolbarStorage(max_request_history)
    app[APP_KEY]['exc_history'] = ExceptionHistory()
    app[APP_KEY]['pdtb_token'] = hexlify(os.urandom(10))
    intercept_exc = settings_opt('intercept_exc')
    if intercept_exc:
        app[APP_KEY]['exc_history'].eval_exc = intercept_exc == 'debug'
