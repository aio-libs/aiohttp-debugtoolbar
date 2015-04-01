import binascii
from functools import partial
from itertools import islice
from collections import deque
import ipaddress
import aiohttp_mako

APP_KEY = 'aiohttp_debugtollbar'
TEMPLATE_KEY = 'aiohttp_debugtollbar_mako'

REDIRECT_CODES = (301, 302, 303, 304)
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
    Code borrowed from: http://forums.devshed.com/python-programming-11/case-insensitive-string-replace-490921.html
    """
    no_case = string.lower()
    index = no_case.rfind(target.lower())
    if index >= 0:
        return string[:index] + replacement + string[index + len(target):]
    else: # no results so return the original string
        return string

render = partial(aiohttp_mako.render_string, app_key=TEMPLATE_KEY)
