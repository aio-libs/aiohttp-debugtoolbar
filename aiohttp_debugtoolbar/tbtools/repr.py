"""werkzeug.debug.repr

This module implements object representations for debugging purposes.
Unlike the default repr these reprs expose a lot more information and
produce HTML instead of ASCII.

Together with the CSS and JavaScript files of the debugger this gives
a colorful and more compact output.

:copyright: (c) 2011 by the Werkzeug Team, see AUTHORS for more details.
:license: BSD.
"""
import re
import sys
from collections import deque
from contextlib import suppress
from functools import partialmethod
from traceback import format_exception_only

from ..tbtools import text_
from ..utils import escape

missing = object()
_paragraph_re = re.compile(r"(?:\r\n|\r|\n){2,}")
RegexType = type(_paragraph_re)


HELP_HTML = """\
<div class="box">
  <h3>%(title)s</h3>
  <pre class="help">%(text)s</pre>
</div>\
"""
OBJECT_DUMP_HTML = """\
<div class="box">
  <h3>%(title)s</h3>
  %(repr)s
  <table>%(items)s</table>
</div>\
"""


def debug_repr(obj):
    """Creates a debug repr of an object as HTML unicode string."""
    return DebugReprGenerator().repr(obj)


def dump(obj=missing):
    """Print the object details to stdout._write (for the interactive
    console of the web debugger.
    """
    gen = DebugReprGenerator()
    if obj is missing:
        rv = gen.dump_locals(sys._getframe(1).f_locals)
    else:
        rv = gen.dump_object(obj)
    sys.stdout._write(rv)


class _Helper:
    """Displays an HTML version of the normal help, for the interactive
    debugger only because it requires a patched sys.stdout.
    """

    def __repr__(self):
        return "Type help(object) for help about object."

    def __call__(self, topic=None):
        if topic is None:
            sys.stdout._write('<span class="help">%s</span>' % repr(self))
            return
        import pydoc

        pydoc.help(topic)
        rv = text_(sys.stdout.reset(), "utf-8", "ignore")
        paragraphs = _paragraph_re.split(rv)
        if len(paragraphs) > 1:
            title = paragraphs[0]
            text = "\n\n".join(paragraphs[1:])
        else:  # pragma: no cover
            title = "Help"
            text = paragraphs[0]
        sys.stdout._write(HELP_HTML % {"title": title, "text": text})


helper = _Helper()


def _add_subclass_info(inner, obj, bases):
    if isinstance(bases, tuple):
        for base in bases:
            if type(obj) is base:
                return inner
    elif type(obj) is bases:
        return inner
    module = ""

    if obj.__class__.__module__ not in ("builtins", "__builtin__", "exceptions"):
        module = f'<span class="module">{obj.__class__.__module__}.</span>'
    return f"{module}{obj.__class__.__name__}({inner})"


class DebugReprGenerator:
    def __init__(self):
        self._stack = []

    def _proxy(self, left, right, base, obj, recursive):
        if recursive:
            return _add_subclass_info(left + "..." + right, obj, base)
        buf = [left]
        for idx, item in enumerate(obj):
            if idx:
                buf.append(", ")
            buf.append(self.repr(item))
        buf.append(right)
        return _add_subclass_info(text_("".join(buf)), obj, base)

    list_repr = partialmethod(_proxy, "[", "]", list)
    tuple_repr = partialmethod(_proxy, "(", ")", tuple)
    set_repr = partialmethod(_proxy, "set([", "])", set)
    frozenset_repr = partialmethod(_proxy, "frozenset([", "])", frozenset)
    deque_repr = partialmethod(
        _proxy, '<span class="module">collections.' "</span>deque([", "])", deque
    )

    def regex_repr(self, obj):
        pattern = text_("'%s'" % str(obj.pattern), "string-escape", "ignore")
        pattern = "r" + pattern
        return text_('re.compile(<span class="string regex">%s</span>)' % pattern)

    def py3_text_repr(self, obj, limit=70):
        buf = ['<span class="string">']
        escaped = escape(obj)
        a = repr(escaped[:limit])
        b = repr(escaped[limit:])
        if b != "''":
            buf.extend((a[:-1], '<span class="extended">', b[1:], "</span>"))
        else:
            buf.append(a)
        buf.append("</span>")
        return _add_subclass_info(text_("".join(buf)), obj, str)

    def py3_binary_repr(self, obj, limit=70):
        buf = ['<span class="string">']
        escaped = escape(text_(obj, "utf-8", "replace"))
        a = repr(escaped[:limit])
        b = repr(escaped[limit:])
        buf.append("b")
        if b != "''":
            buf.extend((a[:-1], '<span class="extended">', b[1:], "</span>"))
        else:
            buf.append(a)
        buf.append("</span>")
        return _add_subclass_info(text_("".join(buf)), obj, bytes)

    def dict_repr(self, d, recursive):
        if recursive:
            return _add_subclass_info(text_("{...}"), d, dict)
        buf = ["{"]
        for idx, (key, value) in enumerate(d.items()):
            if idx:
                buf.append(", ")
            buf.append(
                '<span class="pair"><span class="key">%s</span>: '
                '<span class="value">%s</span></span>'
                % (self.repr(key), self.repr(value))
            )
        buf.append("}")
        return _add_subclass_info(text_("".join(buf)), d, dict)

    def object_repr(self, obj):
        return text_(
            '<span class="object">%s</span>'
            % escape(text_(repr(obj), "utf-8", "replace"))
        )

    def dispatch_repr(self, obj, recursive):
        if obj is helper:
            return text_('<span class="help">%r</span>' % helper)
        if isinstance(obj, (int, float, complex)):
            return text_('<span class="number">%r</span>' % obj)
        if isinstance(obj, str):
            return self.py3_text_repr(obj)
        if isinstance(obj, bytes):
            return self.py3_binary_repr(obj)
        if isinstance(obj, RegexType):
            return self.regex_repr(obj)
        if isinstance(obj, list):
            return self.list_repr(obj, recursive)
        if isinstance(obj, tuple):
            return self.tuple_repr(obj, recursive)
        if isinstance(obj, set):
            return self.set_repr(obj, recursive)
        if isinstance(obj, frozenset):
            return self.frozenset_repr(obj, recursive)
        if isinstance(obj, dict):
            return self.dict_repr(obj, recursive)
        if deque is not None and isinstance(obj, deque):
            return self.deque_repr(obj, recursive)
        return self.object_repr(obj)

    def fallback_repr(self):
        try:
            info = "".join(format_exception_only(*sys.exc_info()[:2]))
        except Exception:  # pragma: no cover
            info = "?"
        r = escape(text_(info, "utf-8", "ignore").strip())
        msg = f'<span class="brokenrepr">&lt;broken repr ({r})&gt;</span>'
        return text_(msg)

    def repr(self, obj):
        recursive = False
        for item in self._stack:
            if item is obj:
                recursive = True
                break
        self._stack.append(obj)
        try:
            return self.dispatch_repr(obj, recursive)
        except Exception:
            return self.fallback_repr()
        finally:
            self._stack.pop()

    def dump_object(self, obj):
        repr = items = None
        if isinstance(obj, dict):
            title = "Contents of"
            items = []
            for key, value in obj.items():
                if not isinstance(key, str):
                    items = None
                    break
                items.append((key, self.repr(value)))
        if items is None:
            items = []
            repr = self.repr(obj)
            for key in dir(obj):
                with suppress(AttributeError):
                    items.append((key, self.repr(getattr(obj, key))))
            title = "Details for"
        title += " " + object.__repr__(obj)[1:-1]
        return self.render_object_dump(items, title, repr)

    def dump_locals(self, d):
        items = [(key, self.repr(value)) for key, value in d.items()]
        return self.render_object_dump(items, "Local variables in frame")

    def render_object_dump(self, items, title, repr=None):
        html_items = []
        for key, value in items:
            html_items.append(
                f'<tr><th>{escape(key)}<td><pre class="repr">{value}</pre>'
            )
        if not html_items:
            html_items.append("<tr><td><em>Nothing</em>")
        return OBJECT_DUMP_HTML % {
            "title": escape(title),
            "repr": repr and '<pre class="repr">%s</pre>' % repr or "",
            "items": "\n".join(html_items),
        }
