.. _tutorial:

===============
Sponge tutorial
===============

Bob, your best friend!
----------------------

Sponge comes with `bob`, a command-line utility that will create the
first project structure for you, and even run your projects.

1. Creating your first project:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run `bob create some-example` on your shell.

Enter in the created directory: `cd some-example`

Run `bob go` on your shell.

Access http://localhost:4000

2. Understanding controllers and routes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sponge's first project has a pretty good example of how works its
routing system.

In a nutshell, all you have to do is using @route decorator.

Example::
        >>> from sponge.controller import route
        >>> from sponge.controller import Controller
        >>> class HelloWorld(Controller):
        ...     @route('say_name', '/say/:some/name')
        ...     def name_controller(self, some):
        ...         return 'Hello %s!' % some

Therefore, you get to configure your project's settings.yml to mount
that controller at some base url::
    host: 127.0.0.1
    port: 8080
    application:
      classes:
        HelloWorld: /awesome/routes
      ...


At this point, if you just access at browser:
   http://127.0.0.1:8080/awesome/routes/say/John/name
   will give you the response:
   "Hello John!"
