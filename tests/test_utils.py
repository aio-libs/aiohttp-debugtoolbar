import os
import sys

from aiohttp_debugtoolbar.utils import addr_in, escape, format_fname


def test_escape():
    assert escape(None) == ""
    assert escape(42) == "42"
    assert escape("<>") == "&lt;&gt;"
    assert escape('"foo"') == '"foo"'
    assert escape('"foo"', True) == "&quot;foo&quot;"


def test_format_fname():
    # test_builtin
    assert format_fname("{a}") == "{a}"

    # test_relpath
    val = "." + os.path.sep + "foo"
    assert format_fname(val) == val

    # test_unknown
    val = ".." + os.path.sep + "foo"
    assert format_fname(val) == "./../foo".replace("/", os.path.sep)


def test_module_file_path():
    sys_path_l = (
        "/foo/",
        "/foo/bar",
        "/usr/local/python/site-packages/",
    )

    prefix = "c:" if sys.platform == "win32" else ""
    sys_path = map(lambda p: prefix + p.replace("/", os.path.sep), sys_path_l)
    modpath = format_fname(
        prefix + "/foo/bar/aiohttp_debugtoolbar/tests/debugfoo.py".replace("/", os.path.sep),
        sys_path,
    )
    expected = "<aiohttp_debugtoolbar/tests/debugfoo.py>".replace("/", os.path.sep)
    assert modpath == expected


def test_no_matching_sys_path():
    val = "/foo/bar/aiohttp_debugtoolbar/foo.py"
    sys_path = [("c:" if sys.platform == "win32" else "") + "/bar/baz"]
    expected = "</foo/bar/aiohttp_debugtoolbar/foo.py>".replace("/", os.path.sep)
    assert format_fname(val, sys_path) == expected


def test_addr_in():
    assert not addr_in("127.0.0.1", [])
    assert addr_in("127.0.0.1", ["127.0.0.1"])
