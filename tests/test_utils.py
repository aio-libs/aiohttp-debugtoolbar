import os
import unittest

from aiohttp_debugtoolbar.utils import escape, format_fname, addr_in


class TestUtils(unittest.TestCase):
    def test_escape(self):
        self.assertEqual(escape(None), '')
        self.assertEqual(escape(42), '42')
        self.assertEqual(escape('<>'), '&lt;&gt;')
        self.assertEqual(escape('"foo"'), '"foo"')
        self.assertEqual(escape('"foo"', True), '&quot;foo&quot;')

    def test_format_fname(self):
        # test_builtin
        self.assertEqual(format_fname('{a}'), '{a}')

        # test_relpath
        val = '.' + os.path.sep + 'foo'
        self.assertEqual(format_fname(val), val)

        # test_unknown
        val = '..' + os.path.sep + 'foo'
        self.assertEqual(format_fname(val),
                         './../foo'.replace('/', os.path.sep))

    def test_module_file_path(self):
        sys_path = [
            '/foo/',
            '/foo/bar',
            '/usr/local/python/site-packages/',
        ]

        sys_path = map(lambda path: path.replace('/', os.path.sep), sys_path)
        modpath = format_fname(
            '/foo/bar/aiohttp_debugtoolbar/tests/debugfoo.py'.replace(
                '/', os.path.sep), sys_path)
        self.assertEqual(modpath,
                         '<aiohttp_debugtoolbar/tests/debugfoo.py>'.replace(
                             '/', os.path.sep))

    def test_no_matching_sys_path(self):
        val = '/foo/bar/aiohttp_debugtoolbar/foo.py'
        sys_path = ['/bar/baz']
        self.assertEqual(format_fname(val, sys_path),
                         '</foo/bar/aiohttp_debugtoolbar/foo.py>')

    def test_addr_in(self):
        self.assertFalse(addr_in('127.0.0.1', []))
        self.assertTrue(addr_in('127.0.0.1', ['127.0.0.1']))
