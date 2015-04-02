import os
import aiohttp_mako

from . import views
from . import panels
from .utils import APP_KEY, TEMPLATE_KEY, STATIC_ROUTE_NAME, hexlify, \
    ToolbarStorage, ExceptionHistory

default_panel_names = {
    'HeaderDebugPanel': panels.HeaderDebugPanel,
    # 'LoggingPanel': panels.LoggingPanel,
    # 'PerformanceDebugPanel': panels.PerformanceDebugPanel,
    # 'RenderingsDebugPanel': panels.RenderingsDebugPanel,
    # 'RequestVarsDebugPanel': panels.RequestVarsDebugPanel,
    # 'SQLADebugPanel': panels.SQLADebugPanel,
    # 'TracebackPanel': panels.TracebackPanel,
    }


default_global_panel_names = {
    # 'IntrospectionDebugPanel': panels.IntrospectionDebugPanel,
    # 'RoutesDebugPanel': panels.RoutesDebugPanel,
    'SettingsDebugPanel': panels.SettingsDebugPanel,
    'TweensDebugPanel': panels.TweensDebugPanel,
    'VersionDebugPanel': panels.VersionDebugPanel,
}


default_settings = {
    # name, convert, default
    'enabled': True,
    'intercept_exc': 'debug', # display or debug
    'intercept_redirects': True,
    'panels': default_panel_names,  # as_globals_list, default_panel_names),
    'extra_panels': [],  # as_globals_list, ()),
    'global_panels': default_global_panel_names,  # as_globals_list, default_global_panel_names),
    'extra_global_panels': [],
    'hosts': ['127.0.0.1'],
    'exclude_prefixes': [],
    'button_style': '',
    'max_request_history': 100,
    'max_visible_requests':  10,
}



def setup(app, **kw):
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))
    app[APP_KEY] = {}
    templates_app = os.path.join(APP_ROOT, 'templates')
    templates_panels = os.path.join(APP_ROOT, 'panels/templates')

    app[APP_KEY]['settings'] = default_settings

    aiohttp_mako.setup(app, input_encoding='utf-8',
                            output_encoding='utf-8',
                            default_filters=['decode.utf8'],
                            directories=[templates_app, templates_panels],
                            app_key=TEMPLATE_KEY)

    static_location = os.path.join(APP_ROOT, 'static')



    app.router.add_static('/_debugtoolbar/static', static_location,
                          name=STATIC_ROUTE_NAME)


    app.router.add_route('GET', '/_debugtoolbarsse', views.sse,
                         name='debugtoolbar.sse')
    # app.router.add_route('GET', '_debug_toolbar/source', views.
    #                      name='debugtoolbar.source')
    # app.router.add_route('GET', '_debug_toolbar/execute',
    #                      name='debugtoolbar.execute')
    # app.router.add_route('GET', '_debug_toolbar/console',
    #                      name='debugtoolbar.console')
    # app.router.add_route('GET', '_debug_toolbar/exception',
    #                      name='debugtoolbar.exception')
    # app.router.add_route('GET', '_debug_toolbar/sqlalchemy/sql_select',
    #                      name='debugtoolbar.sql_select')
    # app.router.add_route('GET', '_debug_toolbar/sqlalchemy/sql_explain',
    #                      name='debugtoolbar.sql_explain')
    app.router.add_route('GET', '/_debugtoolbar/{request_id}',
                         views.request_view,
                         name='debugtoolbar.request')

    app.router.add_route('GET', '/_debugtoolbar',
                         views.request_view,
                         name='debugtoolbar.main')
    # app.router.add_route('GET', '/_debugtoolbar',
    #                      views.request_view,
    #                      name='debugtoolbar')


    def settings_opt(name):
        return app[APP_KEY]['settings'][name]

    max_request_history = settings_opt('max_request_history')

    app[APP_KEY]['request_history'] = ToolbarStorage(max_request_history)
    app[APP_KEY]['exc_history'] = ExceptionHistory()
    app[APP_KEY]['pdtb_token'] = hexlify(os.urandom(10))
    intercept_exc = settings_opt('intercept_exc')
    if intercept_exc:
        app[APP_KEY]['exc_history'].eval_exc = intercept_exc == 'debug'
