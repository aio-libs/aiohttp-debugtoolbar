from urllib.parse import unquote as url_unquote
from aiohttp.web import Response
from .utils import replace_insensitive, STATIC_ROUTE_NAME, APP_KEY


__all__ = ['DebugToolbar']


class DebugToolbar:

    def __init__(self, request, panel_classes, global_panel_classes):
        self.panels = []
        self.global_panels = []
        self.request = request
        self.status = 200

        # Panels can be be activated (more features) (e.g. Performace panel)
        pdtb_active = url_unquote(request.cookies.get('pdtb_active', ''))

        activated = pdtb_active.split(';')
        # XXX
        for panel_class in panel_classes:
            panel_inst = panel_class(request)
            if panel_inst.dom_id in activated and panel_inst.has_content:
                panel_inst.is_active = True
            self.panels.append(panel_inst)

        for panel_class in global_panel_classes:
            panel_inst = panel_class(request)
            if panel_inst.dom_id in activated and panel_inst.has_content:
                panel_inst.is_active = True
            self.global_panels.append(panel_inst)

    @property
    def json(self):
        return {'method': self.request.method,
                'path': self.request.path,
                'scheme': 'http',
                'status_code': self.status}

    async def process_response(self, request, response):
        # if isinstance(response, WSGIHTTPException):
        #  the body of a WSGIHTTPException needs to be "prepared"
        # response.prepare(request.environ)
        for panel in self.panels:
            await panel.process_response(response)
        for panel in self.global_panels:
            await panel.process_response(response)

    def inject(self, request, response):
        """
        Inject the debug toolbar iframe into an HTML response.
        """
        # called in host app
        if not isinstance(response, Response):
            return
        settings = request.app[APP_KEY]['settings']
        response_html = response.body
        route = request.app.router['debugtoolbar.request']
        toolbar_url = route.url_for(request_id=request['id'])

        button_style = settings['button_style']

        css_path = request.app.router[STATIC_ROUTE_NAME].url_for(
            filename='css/toolbar_button.css')

        toolbar_css = toolbar_css_template % {'css_path': css_path}
        toolbar_html = toolbar_html_template % {
            'button_style': button_style,
            'css_path': css_path,
            'toolbar_url': toolbar_url}

        toolbar_html = toolbar_html.encode(response.charset or 'utf-8')
        toolbar_css = toolbar_css.encode(response.charset or 'utf-8')
        response_html = replace_insensitive(
            response_html, b'</head>', toolbar_css + b'</head>')
        response.body = replace_insensitive(
            response_html, b'</body>',
            toolbar_html + b'</body>')


toolbar_css_template = """\
<link rel="stylesheet" type="text/css" href="%(css_path)s">"""

toolbar_html_template = """\
<div id="pDebug">
    <div style="display: block; %(button_style)s" id="pDebugToolbarHandle">
        <a title="Show Toolbar" id="pShowToolBarButton"
           href="%(toolbar_url)s" target="pDebugToolbar">&#171;
           FIXME: Debug Toolbar</a>
    </div>
</div>
"""
