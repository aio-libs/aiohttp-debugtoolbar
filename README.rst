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


Ported Panels
-------------
``HeaderDebugPanel``, ``PerformanceDebugPanel``, ``TracebackPanel``,
``SettingsDebugPanel``, ``MiddlewaresDebugPanel``, ``VersionDebugPanel``,
``RoutesDebugPanel``,  ``RequestVarsDebugPanel``


Help Needed
-----------
Are you an experienced coder looking for a project to contribute to
python/asyncio libraries? This is the project for you!


Install and Configuration
-------------------------
::

    $ pip install aiohttp_debugtoolbar


In order to plug in ``aiohttp_debugtoolbar`` you have to attach middleware to
your ``aiohttp.web.Application``, and call ``aiohttp_debugtoolbar.setup``

.. code:: python

    import aiohttp_debugtoolbar
    app = web.Application(loop=loop,
                           middlewares=[aiohttp_debugtoolbar.middleware])
    aiohttp_debugtoolbar.setup(app)


Full Example
------------

.. code:: python

    import asyncio
    import aiohttp_debugtoolbar
    import aiohttp_mako

    from aiohttp import web


    @aiohttp_mako.template('index.html')
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
        app = web.Application(loop=loop,
                              middlewares=[aiohttp_debugtoolbar.middleware])
        # install aiohttp_debugtoolbar
        aiohttp_debugtoolbar.setup(app)

        # install mako templates
        lookup = aiohttp_mako.setup(app, input_encoding='utf-8',
                                    output_encoding='utf-8',
                                    default_filters=['decode.utf8'])
        template = """
        <html>
            <head>
                <title>${title}</title>
            </head>
            <body>
                <h1>${text}</h1>
                <p>
                  <a href="${app.router['exc_example'].url()}">
                  Exception example</a>
                </p>
            </body>
        </html>
        """
        lookup.put_string('index.html', template)

        app.router.add_route('GET', '/', basic_handler, name='index')
        app.router.add_route('GET', '/exc',
                             exception_handler, name='exc_example')

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


Play With Demo
--------------

https://github.com/aio-libs/aiohttp_debugtoolbar/tree/master/demo

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
