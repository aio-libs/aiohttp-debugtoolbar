import binascii
import ipaddress
import os
import sys

from collections import deque
from itertools import islice

APP_KEY = 'aiohttp_debugtoolbar'
TEMPLATE_KEY = 'aiohttp_debugtoolbar_jinja2'

REDIRECT_CODES = (300, 301, 302, 303, 305, 307, 308)
STATIC_PATH = 'static/'
ROOT_ROUTE_NAME = 'debugtoolbar.main'
STATIC_ROUTE_NAME = 'debugtoolbar.static'
EXC_ROUTE_NAME = 'debugtoolbar.exception'


def hexlify(value):
    # value must be int or bytes
    if isinstance(value, int):
        value = bytes(str(value), encoding='utf-8')
    return str(binascii.hexlify(value), encoding='utf-8')


# TODO: refactor to simpler container or change to ordered dict
class ToolbarStorage(deque):
    """Deque for storing Toolbar objects."""

    def __init__(self, max_elem):
        super(ToolbarStorage, self).__init__([], max_elem)

    def get(self, request_id, default=None):
        dict_ = dict(self)
        return dict_.get(request_id, default)

    def put(self, request_id, request):
        self.appendleft((request_id, request))

    def last(self, num_items):
        """Returns the last `num_items` Toolbar objects"""
        return list(islice(self, 0, num_items))


class ExceptionHistory:

    def __init__(self):
        self.frames = {}
        self.tracebacks = {}
        self.eval_exc = 'show'


def addr_in(addr, hosts):
    for host in hosts:
        if ipaddress.ip_address(addr) in ipaddress.ip_network(host):
            return True
    return False


def replace_insensitive(string, target, replacement):
    """Similar to string.replace() but is case insensitive
    Code borrowed from: http://forums.devshed.com/python-programming-11/
    case-insensitive-string-replace-490921.html
    """
    no_case = string.lower()
    index = no_case.rfind(target.lower())
    if index >= 0:
        return string[:index] + replacement + string[index + len(target):]
    else:  # no results so return the original string
        return string


def render(template_name, app, context, *, app_key=TEMPLATE_KEY, **kw):

    lookup = app[app_key]
    template = lookup.get_template(template_name)
    c = context.copy()
    c.update(kw)
    txt = template.render(**c)
    return txt


def common_segment_count(path, value):
    """Return the number of path segments common to both"""
    i = 0
    if len(path) <= len(value):
        for x1, x2 in zip(path, value):
            if x1 == x2:
                i += 1
            else:
                return 0
    return i


def format_fname(value, _sys_path=None):
    if _sys_path is None:
        _sys_path = sys.path  # dependency injection
    # If the value is not an absolute path, the it is a builtin or
    # a relative file (thus a project file).
    if not os.path.isabs(value):
        if value.startswith(('{', '<')):
            return value
        if value.startswith('.' + os.path.sep):
            return value
        return '.' + os.path.sep + value

    # Loop through sys.path to find the longest match and return
    # the relative path from there.
    prefix_len = 0
    value_segs = value.split(os.path.sep)
    for path in _sys_path:
        count = common_segment_count(path.split(os.path.sep), value_segs)
        if count > prefix_len:
            prefix_len = count
    return '<%s>' % os.path.sep.join(value_segs[prefix_len:])


def escape(s, quote=False):
    """Replace special characters "&", "<" and ">" to HTML-safe sequences.  If
    the optional flag `quote` is `True`, the quotation mark character is
    also translated.

    There is a special handling for `None` which escapes to an empty string.

    :param s: the string to escape.
    :param quote: set to true to also escape double quotes.
    """
    if s is None:
        return ''

    if not isinstance(s, (str, bytes)):
        s = str(s)
    if isinstance(s, bytes):
        try:
            s.decode('ascii')
        except UnicodeDecodeError:
            s = s.decode('utf-8', 'replace')
    s = s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    if quote:
        s = s.replace('"', "&quot;")
    return s


class ContextSwitcher:
    """This object is alternative to *await*. It is useful in cases
    when you need to track context switches inside coroutine.

    see: https://www.python.org/dev/peps/pep-0380/#formal-semantics
    """
    def __init__(self):
        self._on_context_switch_out = []
        self._on_context_switch_in = []

    def add_context_in(self, callback):
        assert callable(callback), 'callback should be callable'
        self._on_context_switch_in.append(callback)

    def add_context_out(self, callback):
        assert callable(callback), 'callback should be callable'
        self._on_context_switch_out.append(callback)

    def __call__(self, expr):
        def iterate():
            for callbale in self._on_context_switch_in:
                callbale()

            _i = iter(expr.__await__())
            try:
                _y = next(_i)
            except StopIteration as _e:
                _r = _e.value
            else:
                while 1:
                    try:
                        for callbale in self._on_context_switch_out:
                            callbale()
                        _s = yield _y
                        for callbale in self._on_context_switch_in:
                            callbale()
                    except GeneratorExit as _e:
                        try:
                            _m = _i.close
                        except AttributeError:
                            pass
                        else:
                            _m()
                        raise _e
                    except BaseException as _e:
                        _x = sys.exc_info()
                        try:
                            _m = _i.throw
                        except AttributeError:
                            raise _e
                        else:
                            try:
                                _y = _m(*_x)
                            except StopIteration as _e:
                                _r = _e.value
                                break
                    else:
                        try:
                            if _s is None:
                                _y = next(_i)
                            else:
                                _y = _i.send(_s)
                        except StopIteration as _e:
                            _r = _e.value
                            break
            result = _r
            for callbale in self._on_context_switch_out:
                callbale()
            return result

        return _Coro(iterate())


class _Coro:
    __slots__ = ('_it')

    def __init__(self, it):
        self._it = it

    def __await__(self):
        return self._it
