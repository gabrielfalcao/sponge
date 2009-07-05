.. _view:

===================
Sponge view helpers
===================

Sponge uses Genshi_ as template language.

To renderize your html files, use the render_html function::

   >>> import cherrypy
   >>> from sponge.view import render_html
   >>>
   >>> class MyController:
   ...      @cherrypy.expose
   ...      def index(self):
   ...          return render_html('index.html', {'variable1': range(10),
                                                  'variable2': 'Hello World'})
   ...

Arguments:

 * filename: the template file name
 * context: a dictionary with the variables to send to template

Optional Arguments:

 * template_path: the path containing the given template name, defaults to 'view.dir' <configuration> CherryPy_'s config.'

A minor, but actual issue when building websites with CherryPy_ is to build fullpath urls within your templates, it can be done with the make_url function::

   >>> from sponge.view import make_url
   >>>
   >>> make_url('/media/css/base.css')
   'http://localhost:8080/media/css/base.css'

make_url also add slash when is nedded::

   >>> from sponge.view import make_url
   >>>
   >>> make_url('media/js/jquery.js')
   'http://localhost:8080/media/js/jquery.js'

The examples above mocks the CherryPy_ server, as it would be running on localhost, port 8080, but whenever you run CherryPy_, make_url works as expected.

Arguments:

 * url: the url to join with server address

If you want to build a application that handles images, you can use jpeg function to render them::

   >>> import cherrypy
   >>> from sponge.view import jpeg
   >>>
   >>> class MyController:
   ...      @cherrypy.expose
   ...      def image_jpg(self):
   ...          return jpeg('images/logo.jpg')
   ...

Arguments:

 * path: the image relative path to 'image.dir' configuration variable.

Optional Arguments:

 * base_path: the path containing the given image path, defaults to 'image.dir' <configuration> CherryPy_'s config.'


:: _Genshi: http://genshi.edgewall.org/
.. _CherryPy: http://www.cherrypy.org/