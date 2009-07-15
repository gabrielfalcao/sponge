.. _image:

====================
sponge image helpers
====================

If you want to build a application that handles images, you can use ``jpeg(path)`` function to render them::

   >>> import cherrypy
   >>> from sponge.image import jpeg
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
   >>> from sponge.image import picture
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
