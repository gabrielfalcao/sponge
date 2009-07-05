.. _configuration:

====================
sponge configuration
====================

There are a few variables to set within cherrypy.config dictionary to Sponge work properly:

 * ``view.dir``: A string containing the absolute path to your html path.
 * ``image.dir``: A string containing the absolute path to where look for pictures and render as http response in sponge.view.jpeg and sponge.view.picture.

Those variables just need to be set in cherrypy.config dict.

Example::

   >>> import cherrypy
   >>> from os.path import join, abspath, dirname
   >>> cherrypy.config['view.dir'] = '/home/username/projects/webapp1/templates/html'
   >>> # or even
   >>> cherrypy.config['view.dir'] = abspath(join(dirname("."), 'templates/html'))