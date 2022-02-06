import platform
import sys

import pytest


@pytest.mark.skipif(
    not sys.platform.startswith("linux") or platform.python_implementation() == "PyPy",
    reason="Unreliable",
)
def test_import_time(pytester: pytest.Pytester) -> None:
    """Check that importing aiohttp-debugtoolbar doesn't take too long.
    Obviously, the time may vary on different machines and may need to be adjusted
    from time to time, but this should provide an early warning if something is
    added that significantly increases import time.
    """
    r = pytester.run(
        sys.executable, "-We", "-c", "import aiohttp_debugtoolbar", timeout=0.6
    )

    assert not r.stdout.str()
    assert not r.stderr.str()
