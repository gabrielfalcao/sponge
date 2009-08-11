.. _contrib:

==============
Sponge contrib
==============

Controllers
===========

Sponge has contrib controllers, which you can just use inside your own
controllers.

Image Handler
-------------

Sponge has the ``ImageHandler`` class, which is a CherryPy controller that handles dinamically resized and cropped images.
It is made through the :ref:`view' ``picture``.

Example::

   >>> import cherrypy
   >>> from sponge.contrib.controllers import ImageHandler
   >>>
   >>> class MyController:
   ...      exposed = True
   ...      images = ImageHandler()
   ...      def index(self):
   ...          return 'try out going to /images/crop/200x200/logo.jpg'

Possible routes
^^^^^^^^^^^^^^^

Considering that:
 * You have configured the cherrypy.config['image.dir'] to '/home/user/images'
 * You are using the example above

Then
 * /images/path/to/cat.jpg - would serve the file ``"/home/user/images/path/to/cat.jpg"`` as is.
 * /images/dog.jpg - would serve the file ``"/home/user/images/dog.jpg"`` as is.
 * /images/crop/200x200/dog.jpg - would serve the file ``"/home/user/images/dog.jpg"`` cropped and resized to 200 x 200 pixels.
 * /images/crop/90x80/another/path/image.jpg - would serve the file ``"/home/user/images/another/path/image.jpg"`` cropped and resized to 90 x 80 pixels.

Caching
^^^^^^^

ImageHandler support caching of generated images, all you need is to
set the cache path on its instantiation, and the path must exist.

Example::

   >>> import cherrypy
   >>> from sponge.contrib.controllers import ImageHandler
   >>>
   >>> class MyController:
   ...      exposed = True
   ...      images = ImageHandler(cache_at='/srv/images/content')
   ...      def index(self):
   ...          return 'try out going to /images/crop/200x200/logo.jpg'

Sponge's ImageHandler will lookup in the given directory if the image
exists, then it serves statically directly from disk.  If the file is
not cached, ImageHandler will generate the image, save on disk and
serve.