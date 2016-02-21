import asyncio
import json
import aiohttp_jinja2

from aiohttp import web

# from .tbtools.console import _ConsoleFrame
from .utils import TEMPLATE_KEY, APP_KEY, ROOT_ROUTE_NAME, STATIC_ROUTE_NAME


@aiohttp_jinja2.template('toolbar.jinja2', app_key=TEMPLATE_KEY)
def request_view(request):
    settings = request.app[APP_KEY]['settings']
    history = request.app[APP_KEY]['request_history']

    try:
        last_request_pair = history.last(1)[0]
    except IndexError:
        last_request_id = None
    else:
        last_request_id = last_request_pair[0]

    request_id = request.match_info.get('request_id', last_request_id)

    toolbar = history.get(request_id, None)

    panels = toolbar.panels if toolbar else []
    global_panels = toolbar.global_panels if toolbar else []

    static_path = request.app.router[STATIC_ROUTE_NAME].url(filename='')
    root_path = request.app.router[ROOT_ROUTE_NAME].url()

    button_style = settings.get('button_style', '')
    max_visible_requests = settings['max_visible_requests']

    hist_toolbars = history.last(max_visible_requests)

    return {'panels': panels,
            'static_path': static_path,
            'root_path': root_path,
            'button_style': button_style,
            'history': hist_toolbars,
            'global_panels': global_panels,
            'request_id': request_id,
            'request': toolbar.request if toolbar else None}


class ExceptionDebugView:

    def _validate_token(self, request):
        exc_history = self._exception_history(request)
        token = request.GET.get('token')

        if exc_history is None:
            raise web.HTTPBadRequest(text='No exception history')
        if not token:
            raise web.HTTPBadRequest(text='No token in request')
        if not (token == request.app[APP_KEY]['pdtb_token']):
            raise web.HTTPBadRequest(text='Bad token in request')

    def _exception_history(self, request):
        return request.app[APP_KEY]['exc_history']

    def _get_frame(self, request):
        frm = request.GET.get('frm')
        if frm is not None:
            frm = int(frm)
        return frm

    @asyncio.coroutine
    def _get_tb(self, request):
        yield from request.read()
        tb = request.GET.get('tb')
        if not tb:
            yield from request.post()
            tb = request.POST.get('tb')
        if tb is not None:
            tb = int(tb)
        return tb

    @asyncio.coroutine
    def _get_cmd(self, request):
        yield from request.read()
        cmd = request.GET.get('cmd')
        if not cmd:
            yield from request.post()
            cmd = request.POST.get('cmd')
        return cmd

    @asyncio.coroutine
    def exception(self, request):
        self._validate_token(request)
        tb_id = yield from self._get_tb(request)
        tb = self._exception_history(request).tracebacks[tb_id]
        body = tb.render_full(request).encode('utf-8', 'replace')
        response = web.Response(status=200)
        response.body = body
        return response

    @asyncio.coroutine
    def source(self, request):
        self._validate_token(request)
        exc_history = self._exception_history(request)
        _frame = self._get_frame(request)
        if _frame is not None:
            frame = exc_history.frames.get(_frame)
            if frame is not None:
                # text = frame.render_source()
                in_frame = frame.get_in_frame_range()
                text = json.dumps({
                    'line': frame.lineno,
                    'inFrame': in_frame,
                    'source': '\n'.join(frame.sourcelines)
                })
                return web.Response(text=text,
                                    content_type='application/json')
        return web.HTTPBadRequest()

    @asyncio.coroutine
    def execute(self, request):
        self._validate_token(request)

        _exc_history = self._exception_history(request)
        if _exc_history.eval_exc:
            exc_history = _exc_history
            cmd = yield from self._get_cmd(request)
            frame = self._get_frame(request)
            if frame is not None and cmd is not None:
                frame = exc_history.frames.get(frame)
                if frame is not None:
                    result = frame.console.eval(cmd)
                    return web.Response(text=result, content_type='text/html')
        return web.HTTPBadRequest()

    # TODO: figure out how to enable console mode on frontend
    # @aiohttp_jinja2.template('console.jinja2',  app_key=TEMPLATE_KEY)
    # def console(self, request):
    #     self._validate_token(request)
    #     static_path = request.app.router[STATIC_ROUTE_NAME].url(filename='')
    #     root_path = request.app.router[ROOT_ROUTE_NAME].url()
    #     token = request.GET.get('token')
    #     tb = yield from self._get_tb(request)
    #
    #     _exc_history = self._exception_history(request)
    #     vars = {
    #         'evalex': _exc_history.eval_exc and 'true' or 'false',
    #         'console': 'true',
    #         'title': 'Console',
    #         'traceback_id': tb or -1,
    #         'root_path': root_path,
    #         'static_path': static_path,
    #         'token': token,
    #         }
    #     if 0 not in _exc_history.frames:
    #         _exc_history.frames[0] = _ConsoleFrame({})
    #     return vars


U_SSE_PAYLOAD = "id: {0}\nevent: new_request\ndata: {1}\n\n"


@asyncio.coroutine
def sse(request):
    response = web.Response(status=200)
    response.content_type = 'text/event-stream'
    history = request.app[APP_KEY]['request_history']
    response.text = ''

    active_request_id = str(request.match_info.get('request_id'))
    client_last_request_id = str(request.headers.get('Last-Event-Id', 0))

    settings = request.app[APP_KEY]['settings']
    max_visible_requests = settings['max_visible_requests']

    if history:
        last_request_pair = history.last(1)[0]
        last_request_id = last_request_pair[0]
        if not last_request_id == client_last_request_id:
            data = []
            for _id, toolbar in history.last(max_visible_requests):
                req_type = 'active' if active_request_id == _id else ''
                data.append([_id, toolbar.json, req_type])

            if data:
                response.text = U_SSE_PAYLOAD.format(last_request_id,
                                                     json.dumps(data))
    return response
