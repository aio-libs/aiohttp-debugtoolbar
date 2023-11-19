import secrets
from pathlib import Path
from typing import Iterable, Literal, Sequence, Type, TypedDict, Union

import aiohttp_jinja2
import jinja2
from aiohttp import web

from . import panels, views
from .middlewares import middleware
from .panels.base import DebugPanel
from .utils import (
    APP_KEY,
    AppState,
    ExceptionHistory,
    STATIC_ROUTE_NAME,
    TEMPLATE_KEY,
    ToolbarStorage,
    _Config,
)
from .views import ExceptionDebugView

default_panel_names = (
    panels.HeaderDebugPanel,
    panels.PerformanceDebugPanel,
    panels.RequestVarsDebugPanel,
    panels.TracebackPanel,
    panels.LoggingPanel,
)


default_global_panel_names = (
    panels.RoutesDebugPanel,
    panels.SettingsDebugPanel,
    panels.MiddlewaresDebugPanel,
    panels.VersionDebugPanel,
)


class _AppDetails(TypedDict):
    exc_history: ExceptionHistory
    pdtb_token: str
    request_history: ToolbarStorage
    settings: _Config


def setup(
    app: web.Application,
    *,
    enabled: bool = True,
    intercept_exc: Literal["debug", "display", False] = "debug",
    intercept_redirects: bool = True,
    panels: Iterable[Type[DebugPanel]] = default_panel_names,
    extra_panels: Iterable[Type[DebugPanel]] = (),
    extra_templates: Union[str, Path, Iterable[Union[str, Path]]] = (),
    global_panels: Iterable[Type[DebugPanel]] = default_global_panel_names,
    hosts: Sequence[str] = ("127.0.0.1", "::1"),
    exclude_prefixes: Iterable[str] = (),
    check_host: bool = True,  # disable host check
    button_style: str = "",
    max_request_history: int = 100,
    max_visible_requests: int = 10,
    path_prefix: str = "/_debugtoolbar",
) -> None:
    config = _Config(
        enabled=enabled,
        intercept_exc=intercept_exc,
        intercept_redirects=intercept_redirects,
        panels=tuple(panels),
        extra_panels=tuple(extra_panels),
        global_panels=tuple(global_panels),
        hosts=hosts,
        exclude_prefixes=tuple(exclude_prefixes),
        check_host=check_host,
        button_style=button_style,
        max_visible_requests=max_visible_requests,
        path_prefix=path_prefix,
    )

    if middleware not in app.middlewares:
        app.middlewares.append(middleware)

    APP_ROOT = Path(__file__).parent
    templates_app = APP_ROOT / "templates"
    templates_panels = APP_ROOT / "panels/templates"

    if isinstance(extra_templates, (str, Path)):
        templ: Iterable[Union[str, Path]] = (extra_templates,)
    else:
        templ = extra_templates
    loader = jinja2.FileSystemLoader((templates_app, templates_panels, *templ))
    aiohttp_jinja2.setup(app, loader=loader, app_key=TEMPLATE_KEY)

    static_location = APP_ROOT / "static"

    exc_handlers = ExceptionDebugView()

    app.router.add_static(
        path_prefix + "/static", static_location, name=STATIC_ROUTE_NAME
    )

    app.router.add_route(
        "GET", path_prefix + "/source", exc_handlers.source, name="debugtoolbar.source"
    )
    app.router.add_route(
        "GET",
        path_prefix + "/execute",
        exc_handlers.execute,
        name="debugtoolbar.execute",
    )
    # app.router.add_route('GET', path_prefix + '/console',
    # exc_handlers.console,
    #                      name='debugtoolbar.console')
    app.router.add_route(
        "GET",
        path_prefix + "/exception",
        exc_handlers.exception,
        name="debugtoolbar.exception",
    )
    # TODO: fix when sql will be ported
    # app.router.add_route('GET', path_prefix + '/sqlalchemy/sql_select',
    #                      name='debugtoolbar.sql_select')
    # app.router.add_route('GET', path_prefix + '/sqlalchemy/sql_explain',
    #                      name='debugtoolbar.sql_explain')

    app.router.add_route(
        "GET", path_prefix + "/sse", views.sse, name="debugtoolbar.sse"
    )

    app.router.add_route(
        "GET",
        path_prefix + "/{request_id}",
        views.request_view,
        name="debugtoolbar.request",
    )
    app.router.add_route(
        "GET", path_prefix, views.request_view, name="debugtoolbar.main"
    )

    app[APP_KEY] = AppState(
        {
            "exc_history": ExceptionHistory(),
            "pdtb_token": secrets.token_hex(10),
            "request_history": ToolbarStorage(max_request_history),
            "settings": config,
        }
    )
    if intercept_exc:
        app[APP_KEY]["exc_history"].eval_exc = intercept_exc == "debug"
