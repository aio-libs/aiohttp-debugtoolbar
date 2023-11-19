=======
CHANGES
=======

.. towncrier release notes start

0.6.1 (2023-11-19)
==================

- Filtered out requests to debugtoolbar itself from the requests history.
- Improved import time by delaying loading of package data.
- Fixed static URLs when using yarl 1.9+.
- Fixed a warning in the ``re`` module.
- Switched to ``aiohttp.web.AppKey`` for aiohttp 3.9.
- Dropped Python 3.7 and added Python 3.11.

0.6.0 (2020-01-25)
==================

- Fixed ClassBasedView support. #207
- Dropped aiohttp<3.3 support.
- Dropped Python 3.4 support.
- Dropped ``yield from`` and ``@asyncio.coroutine`` support.

0.5.0 (2018-02-14)
==================

- Added safe filter to render_content. #195
- Added support for aiohtp 3.

0.4.1 (2017-08-30)
==================

- Fixed issue with redirects without location header. #174

0.4.0 (2017-05-04)
==================

- Added asyncio trove classifier.
- Addes support for aiohttp 2.0.7+.

0.3.0 (2016-11-18)
==================

- Fixed middleware route finding when using sub-apps. #65
- Added examples for extra panels: pgsql & redis monitor. #59

0.2.0 (2016-11-08)
==================

- Refactored test suite.

0.1.4 (2016-11-07)
==================

- Renamed to aiohttp-debugtoolbar.
- Fixed imcompatibility with aiohttp 1.1.

0.1.3 (2016-10-27)
==================

- Fixed a link to request info page, sort request information alphabetically. #52

0.1.2 (2016-09-27)
==================

- Fixed empty functions names in performance panel. #43 (Thanks @kammala!)
- Fixed flashing message during page rendering issue. #46

0.1.1 (2016-02-21)
==================

- Fixed a demo.
- Added syntax highlight in traceback view, switched highlighter from
  highlight.js to prism.js. #31

0.1.0 (2016-02-13)
==================

- Added Python 3.5 support. (Thanks @stormandco!)
- Added view source button in RoutesDebugPanel. (Thanks @stormandco!)
- Dropped support for Python 3.3. (Thanks @sloria!)
- Added middleware in setup method. (Thanks @sloria!)
- Fixed bug with interactive console.
- Fixed support for aiohttp>=0.21.1.

0.0.5 (2015-09-13)
==================

- Fixed IPv6 socket family error. (Thanks @stormandco!)

0.0.4 (2015-09-05)
==================

- Fixed support for aiohttp>=0.17. (Thanks @himikof!)

0.0.3 (2015-07-03)
==================

- Switched template engine from mako to jinja2. (Thanks @iho!)
- Added custom *yield from* to track context switches inside coroutine.
- Implemented panel for collecting request log messages.
- Disable toolbar code injecting for non web.Response answers
  (StreamResponse or WebSocketResponse for example). #12

0.0.2 (2015-05-26)
==================

- Redesigned UI look-and-feel.
- Renamed `toolbar_middleware_factory` to just `middleware`.

0.0.1 (2015-05-18)
==================

- Initial release.
