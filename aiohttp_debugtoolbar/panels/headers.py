import asyncio
from .base import DebugPanel

__all__ = ['HeaderDebugPanel']
_ = lambda x: x


class HeaderDebugPanel(DebugPanel):
    """
    A panel to display HTTP request and response headers.
    """
    name = 'Header'
    has_content = True
    template = 'headers.dbtmako'
    title = _('HTTP Headers')
    nav_title = title

    def __init__(self, request):
        super().__init__(request)
        self._request_headers = [(k, v) for k, v in
                                 sorted(request.headers.items())]

    @asyncio.coroutine
    def process_response(self, response):
        response_headers = [(k, v) for k, v in
                            sorted(response.headers.items())]
        self.data = {'request_headers': self._request_headers,
                     'response_headers': response_headers}
