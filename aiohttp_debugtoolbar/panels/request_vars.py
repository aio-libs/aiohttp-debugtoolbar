import asyncio
from pprint import saferepr

from .base import DebugPanel


__all__ = ['RequestVarsDebugPanel']


class RequestVarsDebugPanel(DebugPanel):
    """
    A panel to display request variables (POST/GET, session, cookies, and
    ad-hoc request attributes).
    """
    name = 'RequestVars'
    has_content = True
    template = 'request_vars.jinja2'
    title = 'Request Vars'
    nav_title = title

    def __init__(self, request):
        super().__init__(request)

    @asyncio.coroutine
    def process_response(self, response):
        self.data = data = {}
        request = self.request
        yield from request.post()
        data.update({
            'get': [(k, request.GET.getall(k)) for k in request.GET],
            'post': [(k, saferepr(v)) for k, v in request.POST.items()],
            'cookies': [(k, request.cookies.get(k)) for k in request.cookies],
            'attrs': [(k, v) for k, v in request.items()],
        })
        # TODO: think about adding aiohttp_sessions support as separate table
        # and maybe aiohttp_security

        # if hasattr(request, 'session'):
        #     data.update({
        #         'session': dictrepr(request.session),
        #     })
