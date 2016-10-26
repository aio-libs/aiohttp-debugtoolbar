import asyncio
from aiohttp_session import get_session
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

        # TODO: think about aiohttp_security

        # session to separate table
        session = yield from get_session(request)
        if not session.empty:
            data.update({
                'session': [(k, session[k]) for k in session],
            })
