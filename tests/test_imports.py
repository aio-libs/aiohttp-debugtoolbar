import platform
import sys

import pytest


@pytest.mark.skipif(platform.python_implementation() == "PyPy", reason="Too slow")
def test_import_time(pytester: pytest.Pytester) -> None:
    """Check that importing aiohttp-debugtoolbar doesn't take too long.
    Obviously, the time may vary on different machines and may need to be adjusted
    from time to time, but this should provide an early warning if something is
    added that significantly increases import time.
    """
    r = pytester.run(
        sys.executable, "-We", "-c", "import aiohttp_debugtoolbar", timeout=1.0
    )

    assert not r.stdout.str()
    assert not r.stderr.str()
