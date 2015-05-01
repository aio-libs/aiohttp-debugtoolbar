aiohttp_debugtoolbar
====================
.. image:: https://travis-ci.org/aio-libs/aiohttp_debugtoolbar.svg?branch=master
    :target: https://travis-ci.org/aio-libs/aiohttp_debugtoolbar
    :alt: |Build status|
.. image:: https://coveralls.io/repos/aio-libs/aiohttp_debugtoolbar/badge.svg
    :target: https://coveralls.io/r/aio-libs/aiohttp_debugtoolbar
    :alt: |Coverage status|


**aiohttp_debugtoolbar** provides a debug toolbar for your aiohttp_
web application.  Library is dirty port of pyramid_debugtoolbar_ and
still in early development stages. Basic functionality has been
ported:

* basic panels
* intercept redirects
* intercept and pretty print exception
* interactive console
* show source code


Ported Panels
-------------
``HeaderDebugPanel``, ``PerformanceDebugPanel``, ``TracebackPanel``,
``SettingsDebugPanel``, ``MiddlewaresDebugPanel``, ``VersionDebugPanel``,
``RoutesDebugPanel``,  ``RequestVarsDebugPanel``

Panels that will be ported
--------------------------
``LoggingPanel`` , ``SQLADebugPanel``,


Help Needed
-----------
* write tests
* increase coverage
* port EventSource to simple ajax calls or websockets
* refactor tbtools module
* port more panels
* port demo app
* add events to aiopg_ and aiomysql_
* update jquery to newer version
* refresh html design
* rethink UI

Play With Demo
--------------

1) clone repository::

    $ git clone git@github.com:aio-libs/aiohttp_debugtoolbar.git

2) create virtual environment, for instance using *virtualenvwraper*::

    $ cd aiohttp_debugtoolbar
    $ mkvirtualenv -p ``which python3` aiohttp_debugtoolbar

3) install `aiohttp_mako`::

    $ pip install git+https://github.com/jettify/aiohttp_mako.git@master

4) install `aiohttp_debugtoolbar` and other dependencies::

    $ pip install -e .

5) run demo.py::

    python3 demo/demo.py

Now you can play with `aiohttp_debugtoolbar` on http://127.0.0.1:9000


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
.. _aiohttp_mako: https://github.com/aio-libs/aiohttp_mako
.. _pyramid_debugtoolbar: https://github.com/Pylons/pyramid_debugtoolbar
