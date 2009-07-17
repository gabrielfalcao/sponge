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
