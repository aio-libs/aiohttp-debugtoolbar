aiohttp_debugtoolbar
====================
.. image:: https://travis-ci.org/aio-libs/aiohttp_debugtoolbar.svg?branch=master
    :target: https://travis-ci.org/aio-libs/aiohttp_debugtoolbar
    :alt: |Build status|
.. image:: https://coveralls.io/repos/aio-libs/aiohttp_debugtoolbar/badge.svg
    :target: https://coveralls.io/r/aio-libs/aiohttp_debugtoolbar
    :alt: |Coverage status|


**aiohttp_debugtoolbar** provides a debug toolbar for your aiohttp_
web application.  Library is port of pyramid_debugtoolbar_ and
still in early development stages. Basic functionality has been
ported:

* basic panels
* intercept redirects
* intercept and pretty print exception
* interactive python console
* show source code

.. image:: https://raw.githubusercontent.com/aio-libs/aiohttp_debugtoolbar/master/demo/aiohttp_debugtoolba_sceenshot.png


Ported Panels
-------------
``HeaderDebugPanel``, ``PerformanceDebugPanel``, ``TracebackPanel``,
``SettingsDebugPanel``, ``MiddlewaresDebugPanel``, ``VersionDebugPanel``,
``RoutesDebugPanel``,  ``RequestVarsDebugPanel``, ``LoggingPanel``


Help Needed
-----------
Are you coder looking for a project to contribute to
python/asyncio libraries? This is the project for you!


Install and Configuration
-------------------------
::

    $ pip install aiohttp_debugtoolbar


In order to plug in ``aiohttp_debugtoolbar``, call
``aiohttp_debugtoolbar.setup`` on your app.

.. code:: python

    import aiohttp_debugtoolbar
    app = web.Application(loop=loop)
    aiohttp_debugtoolbar.setup(app)


Full Example
------------

.. code:: python

    import asyncio
    import jinja2
    import aiohttp_debugtoolbar
    import aiohttp_jinja2

    from aiohttp import web


    @aiohttp_jinja2.template('index.html')
    def basic_handler(request):
        return {'title': 'example aiohttp_debugtoolbar!',
                'text': 'Hello aiohttp_debugtoolbar!',
                'app': request.app}


    @asyncio.coroutine
    def exception_handler(request):
        raise NotImplementedError


    @asyncio.coroutine
    def init(loop):
        # add aiohttp_debugtoolbar middleware to you application
        app = web.Application(loop=loop)
        # install aiohttp_debugtoolbar
        aiohttp_debugtoolbar.setup(app)

        template = """
        <html>
            <head>
                <title>{{ title }}</title>
            </head>
            <body>
                <h1>{{ text }}</h1>
                <p>
                  <a href="{{ app.router['exc_example'].url() }}">
                  Exception example</a>
                </p>
            </body>
        </html>
        """
        # install jinja2 templates
        loader = jinja2.DictLoader({'index.html': template})
        aiohttp_jinja2.setup(app, loader=loader)

        # init routes for index page, and page with error
        app.router.add_route('GET', '/', basic_handler, name='index')
        app.router.add_route('GET', '/exc', exception_handler,
                             name='exc_example')

        handler = app.make_handler()
        srv = yield from loop.create_server(handler, '127.0.0.1', 9000)
        print("Server started at http://127.0.0.1:9000")
        return srv, handler


    loop = asyncio.get_event_loop()
    srv, handler = loop.run_until_complete(init(loop))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(handler.finish_connections())

Thanks!
-------

I've borrowed a lot of code from following projects. I highly
recommend to check them out:

* pyramid_debugtoolbar_
* django-debug-toolbar_
* flask-debugtoolbar_

Play With Demo
--------------

https://github.com/aio-libs/aiohttp_debugtoolbar/tree/master/demo

Requirements
------------

* Python_ 3.4+
* aiohttp_
* aiohttp_jinja2_


.. _Python: https://www.python.org
.. _asyncio: http://docs.python.org/3.4/library/asyncio.html
.. _aiohttp: https://github.com/KeepSafe/aiohttp
.. _aiopg: https://github.com/aio-libs/aiopg
.. _aiomysql: https://github.com/aio-libs/aiomysql
.. _aiohttp_jinja2: https://github.com/aio-libs/aiohttp_jinja2
.. _pyramid_debugtoolbar: https://github.com/Pylons/pyramid_debugtoolbar
.. _django-debug-toolbar: https://github.com/django-debug-toolbar/django-debug-toolbar
.. _flask-debugtoolbar: https://github.com/mgood/flask-debugtoolbar
