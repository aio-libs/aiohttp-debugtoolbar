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

    async def process_response(self, response):
        self.data = data = {}
        request = self.request
        post_data = await request.post()
        data.update({
            'get': [(k, request.query.getall(k))
                    for k in sorted(request.query)],
            'post': [(k, saferepr(post_data.getall(k)))
                     for k in sorted(post_data)],
            'cookies': [(k, v) for k, v in sorted(request.cookies.items())],
            'attrs': [(k, v) for k, v in sorted(request.items())],
        })

        # TODO: think about aiohttp_security

        # session to separate table
        session = request.get('aiohttp_session')
        if session and not session.empty:
            data.update({
                'session': [(k, v) for k, v in sorted(session.items())],
            })
