"""werkzeug.debug.console

Interactive console support.

:copyright: (c) 2011 by the Werkzeug Team, see AUTHORS for more details.
:license: BSD.
"""
import code
import sys
import threading
from types import CodeType

from .repr import debug_repr, dump, helper
from ..utils import escape

_local = threading.local()


class HTMLStringO:
    """A StringO version that HTML escapes on write."""

    def __init__(self):
        self._buffer = []

    def isatty(self):
        return False

    def close(self):
        pass

    def flush(self):
        pass

    def seek(self, n, mode=0):
        pass

    def readline(self):
        if len(self._buffer) == 0:
            return ""
        ret = self._buffer[0]
        del self._buffer[0]
        return ret

    def reset(self):
        val = "".join(self._buffer)
        del self._buffer[:]
        return val

    def _write(self, x):
        if isinstance(x, bytes):
            x = str(x, encoding="utf-8", errors="replace")
        self._buffer.append(x)

    def write(self, x):
        self._write(escape(x))

    def writelines(self, x):
        self._write(escape("".join(x)))


class ThreadedStream:
    """Thread-local wrapper for sys.stdout for the interactive console."""

    @staticmethod
    def push():
        if not isinstance(sys.stdout, ThreadedStream):
            sys.stdout = ThreadedStream()
        _local.stream = HTMLStringO()

    @staticmethod
    def fetch():
        try:
            stream = _local.stream
        except AttributeError:
            return ""
        return stream.reset()

    @staticmethod
    def displayhook(obj):
        try:
            stream = _local.stream
        except AttributeError:
            return _displayhook(obj)
        # stream._write bypasses escaping as debug_repr is
        # already generating HTML for us.
        if obj is not None:
            _local._current_ipy.locals["_"] = obj
            stream._write(debug_repr(obj))

    def __setattr__(self, name, value):
        raise AttributeError("read only attribute %s" % name)

    def __dir__(self):
        return dir(sys.__stdout__)

    def __getattribute__(self, name):
        if name == "__members__":
            return dir(sys.__stdout__)
        try:
            stream = _local.stream
        except AttributeError:
            stream = sys.__stdout__
        return getattr(stream, name)

    def __repr__(self):
        return repr(sys.__stdout__)


# add the threaded stream as display hook
_displayhook = sys.displayhook
sys.displayhook = ThreadedStream.displayhook


class _ConsoleLoader:
    def __init__(self):
        self._storage = {}

    def register(self, code, source):
        self._storage[id(code)] = source
        # register code objects of wrapped functions too.
        for var in code.co_consts:
            if isinstance(var, CodeType):
                self._storage[id(var)] = source

    def get_source_by_code(self, code):
        try:
            return self._storage[id(code)]
        except KeyError:
            pass


def _wrap_compiler(console):
    compile = console.compile

    def func(source, filename, symbol):
        code = compile(source, filename, symbol)
        console.loader.register(code, source)
        return code

    console.compile = func


class _InteractiveConsole(code.InteractiveInterpreter):
    def __init__(self, app, globals, locals):
        self._app = app
        code.InteractiveInterpreter.__init__(self, locals)
        self.globals = dict(globals)
        self.globals["dump"] = dump
        self.globals["help"] = helper
        self.globals["__loader__"] = self.loader = _ConsoleLoader()
        self.more = False
        self.buffer = []
        _wrap_compiler(self)

    def runsource(self, source):
        source = source.rstrip() + "\n"
        ThreadedStream.push()
        prompt = self.more and "... " or ">>> "
        try:
            source_to_eval = "".join(self.buffer + [source])
            if code.InteractiveInterpreter.runsource(
                self, source_to_eval, "<debugger>", "single"
            ):
                self.more = True
                self.buffer.append(source)
            else:
                self.more = False
                del self.buffer[:]
        finally:
            output = ThreadedStream.fetch()
        return prompt + source + output

    def runcode(self, code):
        try:
            exec(code, self.globals, self.locals)  # noqa: S102
        except Exception as exc:
            self.showtraceback(exc)

    def showtraceback(self, exc):
        from .tbtools import get_current_traceback

        tb = get_current_traceback(skip=1, exc=exc, app=self._app)
        sys.stdout._write(tb.render_summary(self._app))

    def showsyntaxerror(self, filename=None):
        from .tbtools import get_current_traceback

        exc = SyntaxError(filename)
        tb = get_current_traceback(skip=6, exc=exc, app=self._app)
        sys.stdout._write(tb.render_summary(self._app))

    def write(self, data):
        sys.stdout.write(data)


class Console:
    """An interactive console."""

    def __init__(self, app, globals=None, locals=None):
        self._app = app
        if locals is None:
            locals = {}
        if globals is None:
            globals = {}
        self._ipy = _InteractiveConsole(app, globals, locals)

    def eval(self, code):
        _local._current_ipy = self._ipy
        old_sys_stdout = sys.stdout
        try:
            return self._ipy.runsource(code)
        finally:
            sys.stdout = old_sys_stdout


class _ConsoleFrame:
    """Helper class so that we can reuse the frame console code for the
    standalone console.
    """

    def __init__(self, namespace, app):
        self.console = Console(namespace, app)
        self.id = 0
