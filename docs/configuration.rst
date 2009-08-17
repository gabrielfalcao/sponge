.. _configuration:

====================
sponge configuration
====================

Sponge's configuration relies in the settings.yml file, which uses
`YAML <http://www.yaml.org/>`_ as format.
The settings.yml file must be in the path you are running Sponge Bob
command line tool.

There are a few options to set in settings.yml dictionary to Sponge
work properly:

run-as
------

Default: ``standalone``

A string that determines in which mode the server will run on.

Possible values
:::::::::::::::


standalone
^^^^^^^^^^

The server will be running by itself, useful in local development environment.

Example::

    run-as: standalone

wsgi
^^^^

The server will be running as WSGI. Useful for production deployment.

Example::

    run-as: wsgi

full example
============

This is a full example for a Sponge's possible configuration::

    run-as: standalone # possible values: standalone, wsgi
    host: 127.0.0.1
    port: 8080
    autoreload: true
    application:
      path: /home/user/projects/web-app/module
      template-dir: /home/user/projects/web-app/html
      image-dir: /home/user/projects/web-app/images
      classes:
        SomeController: /

    databases:
      media: mysql://root@localhost/webapp_media
      general: postgres://root:p4ssword@localhost/webapp_general
      metadata: sqlite:///webapp_metadata.db

extra
-----

You can also provide extra configuration, so that you can use that
extra data from within your application.

In order to do that, just provide a key named "extra" on the body of
your config file.

example
:::::::

Simple usage of "extra" configuration::

    run-as: standalone
    host: 127.0.0.1
    port: 8080
    autoreload: true
    application:
      path: /home/user/projects/web-app/module
      template-dir: /home/user/projects/web-app/html
      image-dir: /home/user/projects/web-app/images
      classes:
        SomeController: /

    extra:
      packages-dir: /home/user/packages
      hardcoded-links:
        Support: http://my-homepage.com/support
        Documentation: http://my-homepage.com/docs


And to use it within the application::

    >>> from cherrypy import config
    >>> links = config['sponge.extra']['hardcoded-links']
    >>> packages_at = config['sponge.extra']['packages-dir']

application
-----------

All your application-related configuration relies under the application configuration key


Parameters:
:::::::::::

path
^^^^

The path to python module or file which contains all the controller classes to be routed.

template-dir
^^^^^^^^^^^^

The path in which sponge will look for genshi templates.

image-dir
^^^^^^^^^

The path in which sponge will look for, and save images. In a
nutshell, `sponge.contrib.controllers.ImageHandler` will use it.

classes
^^^^^^^

A key/value pair configuration in which the "key" is the name of the
class to load, and the "value" is the base path to mount the
controller at.

Example::

    application:
      path: /home/user/projects/web-app/controllers.py
      classes:
        MainController: /
        AjaxController: /ajax
        AdminController: /admin

boot
^^^^

Configuration for a "boot" callable.
It is specially useful for subscribing `cherrypy's plugins <http://www.cherrypy.org/wiki/CustomPlugins>`_.
Takes two parameters: `path` and `callable`.
Sponge will import the module at path, and call callable.

Example:

Supposing that you have the following code at `/home/user/project/core.py::

    >>> import cherrypy
    >>> def prepare_my_app():
    ...     if 'database' not in cherrypy.config:
    ...         print "FATAL: You did not configure the database!"
    ...         raise SystemExit(1)

Then, you could configure at your project settings.yml::

    application:
      path: /home/user/projects/web-app/controllers.py
      classes:
        MainController: /
      boot:
        path: /home/user/project/core.py
        callable: prepare_my_app

So, when you just run `bob go`, the function prepare_my_app() will be called.