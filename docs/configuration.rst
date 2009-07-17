.. _configuration:

====================
sponge configuration
====================

Sponge's configuration relies in the settings.yml file, which uses
YAML_ as format.
The settings.yml file must be in the path you are running Sponge Bob
command line tool.

There are a few options to set in settings.yml dictionary to Sponge
work properly:

run-as
------

Default: ``standalone``

A string that determines in which mode the server will run on.

Possible values:

 * `"standalone"`: The server will be running by itself, useful in
   local development environment.

 * `"wsgi"`: The server will be running as WSGI. Useful for production
   deployment.
