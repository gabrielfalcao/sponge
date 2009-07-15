.. _template:

=======================
sponge template helpers
=======================

Sponge uses `Genshi <http://genshi.edgewall.org/>`_ as template language.

To renderize your html files, use the ``render_html(filename, context)`` function::

   >>> import cherrypy
   >>> from sponge.template import render_html
   >>>
   >>> class MyController:
   ...      @cherrypy.expose
   ...      def index(self):
   ...          return render_html('index.html', {'variable1': range(10),
   ...                                            'variable2': 'Hello World'})

Arguments:

 * filename: the template file name
 * context: a dictionary with the variables to send to template

Optional Arguments:

 * template_path: the path containing the given template name, defaults to 'template.dir' at :ref:`configuration`.

A minor, but actual issue when building websites with `CherryPy <http://www.cherrypy.org/>`_ is to build fullpath urls within your templates, it can be done with the ``make_url(url)`` function::

   >>> from sponge.template import make_url
   >>>
   >>> make_url('/media/css/base.css')
   'http://localhost:8080/media/css/base.css'

make_url also add slash when is nedded::

   >>> from sponge.template import make_url
   >>>
   >>> make_url('media/js/jquery.js')
   'http://localhost:8080/media/js/jquery.js'

The examples above mocks the `CherryPy <http://www.cherrypy.org/>`_ server, as it would be running on localhost, port 8080, but whenever you run `CherryPy <http://www.cherrypy.org/>`_, make_url works as expected.

Arguments:

 * url: the url to join with server address