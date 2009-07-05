.. _view:

===================
sponge view helpers
===================

Sponge uses `Genshi <http://genshi.edgewall.org/>`_ as template language.

To renderize your html files, use the ``render_html(filename, context)`` function::

   >>> import cherrypy
   >>> from sponge.view import render_html
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

 * template_path: the path containing the given template name, defaults to 'view.dir' at :ref:`configuration`.

A minor, but actual issue when building websites with `CherryPy <http://www.cherrypy.org/>`_ is to build fullpath urls within your templates, it can be done with the ``make_url(url)`` function::

   >>> from sponge.view import make_url
   >>>
   >>> make_url('/media/css/base.css')
   'http://localhost:8080/media/css/base.css'

make_url also add slash when is nedded::

   >>> from sponge.view import make_url
   >>>
   >>> make_url('media/js/jquery.js')
   'http://localhost:8080/media/js/jquery.js'

The examples above mocks the `CherryPy <http://www.cherrypy.org/>`_ server, as it would be running on localhost, port 8080, but whenever you run `CherryPy <http://www.cherrypy.org/>`_, make_url works as expected.

Arguments:

 * url: the url to join with server address

If you want to build a application that handles images, you can use ``jpeg(path)`` function to render them::

   >>> import cherrypy
   >>> from sponge.view import jpeg
   >>>
   >>> class MyController:
   ...      @cherrypy.expose
   ...      def image_jpg(self):
   ...          return jpeg('images/logo.jpg')


Arguments:

 * path: the image relative path to `'image.dir' configuration variable <configuration>`_.

Optional Arguments:

 * base_path: the path containing the given image path, defaults to 'image.dir' configuration at :ref:`configuration` `CherryPy <http://www.cherrypy.org/>`_'s config.'

Nevertheless just serving a image won't actually make your website doing something dinamic, for instance, you may need to dinamically crop and/or resize a given image, it can be done throught the function ``picture('logo.png', 320, 240)``

   >>> import cherrypy
   >>> from sponge.view import picture
   >>>
   >>> class MyController:
   ...      @cherrypy.expose
   ...      def logo_jpg(self):
   ...          return picture('images/logo.jpg', 120, 90)


Arguments:

 * path: the image relative path to 'image.dir' configuration variable at :ref:`configuration`.
 * width: the width to resize image to.
 * height: the height to resize image to.

Optional Arguments:

 * crop: a boolean to set if the image should be cropped to fit. Defaults to ``True``.
 * center: a boolean to set if the image should be centered when cropped. Defaults to ``True``.
 * mask: a PIL Image object to use as mask. Defaults to ``None``.
 * background: a hexadecimal number with RGB color to use as background. Defaults to ``0xffffff``.
``
