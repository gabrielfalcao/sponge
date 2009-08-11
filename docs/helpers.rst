.. _helpers:

====================
sponge image helpers
====================

If you want to build a application that handles images, you can use ``jpeg(path)`` function to render them::

   >>> import cherrypy
   >>> from sponge.helpers.image import jpeg
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
   >>> from sponge.helpers.image import picture
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

=========================
Sponge pagination helpers
=========================

Paginator
---------

Sponge took `Django's <http://www.djangoproject.com/>`_ `paginator
<http://docs.djangoproject.com/en/dev/topics/pagination/#topics-pagination>`_,
but added a few more unit tests to keep our 100% code coverage policy.

The classes below are located at `sponge.helpers.pagination`.

The :class:`Paginator` class has this constructor:

.. class:: Paginator(object_list, per_page, orphans=0, allow_empty_first_page=True)

Required arguments
------------------

``object_list``
    A list, tuple or other sliceable object with a
    ``count()`` or ``__len__()`` method.

``per_page``
    The maximum number of items to include on a page, not including orphans
    (see the ``orphans`` optional argument below).

Optional arguments
------------------

``orphans``
    The minimum number of items allowed on the last page, defaults to zero.
    Use this when you don't want to have a last page with very few items.
    If the last page would normally have a number of items less than or equal
    to ``orphans``, then those items will be added to the previous page (which
    becomes the last page) instead of leaving the items on a page by
    themselves. For example, with 23 items, ``per_page=10``, and
    ``orphans=3``, there will be two pages; the first page with 10 items and
    the  second (and last) page with 13 items.

``allow_empty_first_page``
    Whether or not the first page is allowed to be empty.  If ``False`` and
    ``object_list`` is  empty, then an ``EmptyPage`` error will be raised.

Methods
-------

.. method:: Paginator.page(number)

    Returns a :class:`Page` object with the given 1-based index. Raises
    :exc:`InvalidPage` if the given page number doesn't exist.

Attributes
----------

.. attribute:: Paginator.count

    The total number of objects, across all pages.

.. attribute:: Paginator.num_pages

    The total number of pages.

.. attribute:: Paginator.page_range

    A 1-based range of page numbers, e.g., ``[1, 2, 3, 4]``.

``InvalidPage`` exceptions
--------------------------

The ``page()`` method raises ``InvalidPage`` if the requested page is invalid
(i.e., not an integer) or contains no objects. Generally, it's enough to trap
the ``InvalidPage`` exception, but if you'd like more granularity, you can trap
either of the following exceptions:

``PageNotAnInteger``
    Raised when ``page()`` is given a value that isn't an integer.

``EmptyPage``
    Raised when ``page()`` is given a valid value but no objects exist on that
    page.

Both of the exceptions are subclasses of ``InvalidPage``, so you can handle
them both with a simple ``except InvalidPage``.


``Page`` objects
----------------

.. class:: Page(object_list, number, paginator):

You usually won't construct :class:`Pages <Page>` by hand -- you'll get them
using :meth:`Paginator.page`.


Methods
-------

.. method:: Page.has_next()

    Returns ``True`` if there's a next page.

.. method:: Page.has_previous()

    Returns ``True`` if there's a previous page.

.. method:: Page.has_other_pages()

    Returns ``True`` if there's a next *or* previous page.

.. method:: Page.next_page_number()

    Returns the next page number. Note that this is "dumb" and will return the
    next page number regardless of whether a subsequent page exists.

.. method:: Page.previous_page_number()

    Returns the previous page number. Note that this is "dumb" and will return
    the previous page number regardless of whether a previous page exists.

.. method:: Page.start_index()

    Returns the 1-based index of the first object on the page, relative to all
    of the objects in the paginator's list. For example, when paginating a list
    of 5 objects with 2 objects per page, the second page's :meth:`~Page.start_index`
    would return ``3``.

.. method:: Page.end_index()

    Returns the 1-based index of the last object on the page, relative to all of
    the objects in the paginator's list. For example, when paginating a list of
    5 objects with 2 objects per page, the second page's :meth:`~Page.end_index`
    would return ``4``.

Attributes
----------

.. attribute:: Page.object_list

    The list of objects on this page.

.. attribute:: Page.number

    The 1-based page number for this page.

.. attribute:: Page.paginator

    The associated :class:`Paginator` object.
