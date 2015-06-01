# -*- coding: utf-8 -*-
"""
    werkzeug.debug test
    ~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2011 by the Werkzeug Team, see AUTHORS for more details.
    :license: BSD license.
"""
import re
import sys
import unittest

from aiohttp_debugtoolbar.tbtools.console import HTMLStringO
from aiohttp_debugtoolbar.tbtools.repr import (debug_repr, DebugReprGenerator,
                                               dump, helper)
from aiohttp_debugtoolbar.tbtools import text_


class Test_debug_repr(unittest.TestCase):
    def test_debug_repr(self):
        assert debug_repr([]) == '[]'
        assert debug_repr([1, 2]) == '[<span class="number">1</span>, ' \
                                     '<span class="number">2</span>]'
        assert debug_repr([1, 'test']) == '[<span class="number">1' \
                                          '</span>, <span class="string">' \
                                          '\'test\'</span>]'
        assert debug_repr([None]) == '[<span class="object">None</span>]'
        assert debug_repr(list(range(20))) == (
            '[<span class="number">0</span>, <span class="number">1</span>, '
            '<span class="number">2</span>, <span class="number">3</span>, '
            '<span class="number">4</span>, <span class="number">5</span>, '
            '<span class="number">6</span>, <span class="number">7</span>, '
            '<span class="number">8</span>, <span class="number">9</span>, '
            '<span class="number">10</span>, <span class="number">11</span>, '
            '<span class="number">12</span>, <span class="number">13</span>, '
            '<span class="number">14</span>, <span class="number">15</span>, '
            '<span class="number">16</span>, <span class="number">17</span>, '
            '<span class="number">18</span>, <span class="number">19</span>]'
        )
        assert debug_repr({}) == '{}'
        assert debug_repr({'foo': 42}) == \
            '{<span class="pair"><span class="key">' \
            '<span class="string">\'foo\''\
            '</span></span>: <span class="value"><span class="number">42' \
            '</span></span></span>}'
        result = debug_repr((1, b'zwei', text_('drei')))
        expected = (
            '(<span class="number">1</span>, <span class="string">b\''
            'zwei\'</span>, <span class="string">\'drei\'</span>)')

        assert result == expected

        class Foo(object):
            def __repr__(self):
                return '<Foo 42>'
        assert debug_repr(Foo()) == '<span class="object">&lt;Foo 42&gt;' \
                                    '</span>'

        class MyList(list):
            pass
        tmp = debug_repr(MyList([1, 2]))
        assert tmp == \
            '<span class="module">tests.test_debug.</span>MyList([' \
            '<span class="number">1</span>, <span class="number">2</span>])'

        result = debug_repr(re.compile(r'foo\d'))
        assert result == \
            're.compile(<span class="string regex">r\'foo\\d\'</span>)'
        result = debug_repr(re.compile(text_(r'foo\d')))
        assert result == 're.compile(<span class="string regex">r' \
                         '\'foo\\d\'</span>)'

        assert debug_repr(frozenset('x')) == \
            'frozenset([<span class="string">\'x\'</span>])'
        assert debug_repr(set('x')) == \
            'set([<span class="string">\'x\'</span>])'

        a = [1]
        a.append(a)
        assert debug_repr(a) == '[<span class="number">1</span>, [...]]'

        class Foo(object):
            def __repr__(self):
                1/0

        result = debug_repr(Foo())

        assert 'division' in result


class Test_object_dumping(unittest.TestCase):
    def test_object_dumping(self):
        class Foo(object):
            x = 42
            y = 23

            def __init__(self):
                self.z = 15

        drg = DebugReprGenerator()
        out = drg.dump_object(Foo())
        assert re.search('Details for', out)
        assert re.search('<th>x.*<span class="number">42</span>(?s)', out)
        assert re.search('<th>y.*<span class="number">23</span>(?s)', out)
        assert re.search('<th>z.*<span class="number">15</span>(?s)', out)

        out = drg.dump_object({'x': 42, 'y': 23})
        assert re.search('Contents of', out)
        assert re.search('<th>x.*<span class="number">42</span>(?s)', out)
        assert re.search('<th>y.*<span class="number">23</span>(?s)', out)

        out = drg.dump_object({'x': 42, 'y': 23, 23: 11})
        assert not re.search('Contents of', out)

        out = drg.dump_locals({'x': 42, 'y': 23})
        assert re.search('Local variables in frame', out)
        assert re.search('<th>x.*<span class="number">42</span>(?s)', out)
        assert re.search('<th>y.*<span class="number">23</span>(?s)', out)


class Test_debug_dump(unittest.TestCase):
    def test_debug_dump(self):
        """Test debug dump"""
        old = sys.stdout
        sys.stdout = HTMLStringO()
        try:
            dump([1, 2, 3])
            x = sys.stdout.reset()
            dump()
            y = sys.stdout.reset()
        finally:
            sys.stdout = old

        assert 'Details for list object at' in x
        assert '<span class="number">1</span>' in x
        assert 'Local variables in frame' in y
        assert '<th>x' in y
        assert '<th>old' in y


class Test_debug_help(unittest.TestCase):
    def test_debug_help(self):
        """Test debug help"""
        old = sys.stdout
        sys.stdout = HTMLStringO()
        try:
            helper([1, 2, 3])
            x = sys.stdout.reset()
        finally:
            sys.stdout = old

        assert 'Help on list object' in x
        assert '__delitem__' in x
