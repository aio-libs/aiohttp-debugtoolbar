import re

from .base import DebugPanel
from ..tbtools.tbtools import Traceback
from ..utils import escape, APP_KEY, STATIC_ROUTE_NAME
from ..utils import ROOT_ROUTE_NAME


__all__ = ['TracebackPanel']


class TracebackPanel(DebugPanel):
    name = 'Traceback'
    template = 'traceback.jinja2'
    title = 'Traceback'
    nav_title = title

    def __init__(self, request):
        super().__init__(request)
        self.exc_history = request.app[APP_KEY]['exc_history']

    @property
    def has_content(self):
        if self._request.get('pdbt_tb'):
            return True
        return False

    async def process_response(self, response):
        if not self.has_content:
            return
        traceback = self._request['pdbt_tb']

        exc = escape(traceback.exception)
        summary = Traceback.render_summary(traceback, self._request.app,
                                           include_title=False)
        token = self.request.app[APP_KEY]['pdtb_token']
        url = ''  # self.request.route_url(EXC_ROUTE_NAME, _query=qs)
        evalex = self.exc_history.eval_exc

        self.data = {
            'evalex': evalex and 'true' or 'false',
            'console': 'false',
            'lodgeit_url': None,
            'title': exc,
            'exception': exc,
            'exception_type': escape(traceback.exception_type),
            'summary': summary,
            'plaintext': traceback.plaintext,
            'plaintext_cs': re.sub('-{2,}', '-', traceback.plaintext),
            'traceback_id': traceback.id,
            'token': token,
            'url': url,
        }

    def render_content(self, request):
        return super(TracebackPanel, self).render_content(request)

    def render_vars(self, request):
        static_path = self._request.app.router[STATIC_ROUTE_NAME] \
            .url_for(filename='')
        root_path = self.request.app.router[ROOT_ROUTE_NAME].url_for()
        return {
            'static_path': static_path,
            'root_path': root_path
        }
