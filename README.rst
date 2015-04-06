aiohttp_debugtoolbar
====================
**aiohttp_debugtoolbar** provides a debug toolbar your aiohttp_ web application.
Library is dirty port of pyramid_debugtoolbar_ and still in early development
stages. Basic functionality has been ported:

* basic panels
* intercept redirects
* intercept and pretty print exception (still need cleanup)
* interactive console
* show source code


Ported Panels
-------------
``HeaderDebugPanel``, ``PerformanceDebugPanel``, ``TracebackPanel``,
``SettingsDebugPanel``, ``TweensDebugPanel``, ``VersionDebugPanel``,
``RoutesDebugPanel``

Panels that will be ported
--------------------------
``LoggingPanel``,  ``RequestVarsDebugPanel``, ``SQLADebugPanel``,



Help Needed
-----------
* write tests
* update jquery to newer version
* refresh html design
* rethink UI
* port EvenSouse to simple ajax calls or websockets

* increase coverage
* refactor tbtools module
* port more panels
* port demo app
* add events to aiopg_ and aiomysql_


Requirements
------------

* Python_ 3.3+
* asyncio_ or Python_ 3.4+
* aiohttp_
* aiohttp_mako_


.. _Python: https://www.python.org
.. _asyncio: http://docs.python.org/3.4/library/asyncio.html
.. _aiohttp: https://github.com/KeepSafe/aiohttp
.. _aiopg: https://github.com/aio-libs/aiopg
.. _aiomysql: https://github.com/aio-libs/aiomysql
.. _aiohttp_mako: https://github.com/jettify/aiohttp_mako
.. _pyramid_debugtoolbar: https://github.com/Pylons/pyramid_debugtoolbar
