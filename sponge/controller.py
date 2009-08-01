#!/usr/bin/env python
# -*- coding: utf-8; -*-
#
# Copyright (C) 2009 Gabriel Falcão <gabriel@nacaolivre.org>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.
import re
import Image
import cherrypy
from cherrypy.lib.static import serve_file
from math import ceil
from sponge.core.io import FileSystem
from sponge.image import jpeg, picture

def route(name, route):
    def dec(func):
        conf = {
            name: {
                'route': route,
                'method': func.__name__
            }
        }
        return func, conf

    return dec

class MetaController(type):
    def __init__(cls, name, bases, attrs):
        for attr, value in attrs.items():
            if isinstance(value, tuple) and len(value) is 2:
                method, conf = value
                setattr(cls,attr, method)
                cls.__conf__['routes'].update(conf)
        super(MetaController, cls).__init__(name, bases, attrs)

class Controller(object):
    __metaclass__ = MetaController
    __conf__ = {'routes': {}}

class InvalidCachePath(IOError):
    pass

class ImageHandler(object):
    exposed = True
    should_cache = False
    cache_path = None
    fs = FileSystem()

    def __init__(self, cache_at=None):
        if not isinstance(cache_at, (basestring, type(None))):
            raise TypeError, 'The path given to ImageHandler ' \
                  'to cache must be a string, got %s' % repr(cache_at)

        if cache_at:
            self.should_cache =True
            self.cache_path = cache_at

            if not self.fs.exists(cache_at):
                raise InvalidCachePath, \
                      'The given path (%s) does not exist, ' \
                      'so that ImageHandler can not save ' \
                      'cache files there.' % cache_at

    def get_cache_path(self, path):
        return self.fs.join(self.cache_path, path.lstrip('/'))

    def __call__(self, *args, **kw):
        if len(args) < 1:
            cherrypy.response.status = 404
            return "not found"

        path = "/".join(args)

        image = jpeg(path=path)

        cache_full_path = None

        if self.should_cache:
            cache_full_path = self.get_cache_path(path)
            if self.fs.exists(cache_full_path):
                return serve_file(cache_full_path, 'image/jpeg')

        if len(args) >= 3 and args[0] == 'crop':
            proportion = re.match(r'(?P<width>\d+)x(?P<height>\d+)',
                                  args[1])
            if proportion:
                width = int(proportion.group('width'))
                height = int(proportion.group('height'))

                image = picture(path="/".join(args[2:]),
                                width=width,
                                height=height)

        if self.should_cache:
            dir_path = self.fs.dirname(cache_full_path)
            self.fs.mkdir(dir_path)
            img_file = self.fs.open_raw(cache_full_path, 'w')
            img_file.write(image)
            img_file.close()

        return image

class InvalidPage(Exception):
    pass

class PageNotAnInteger(InvalidPage):
    pass

class EmptyPage(InvalidPage):
    pass

class Paginator(object):
    def __init__(self, object_list, per_page, orphans=0, allow_empty_first_page=True):
        self.object_list = object_list
        self.per_page = per_page
        self.orphans = orphans
        self.allow_empty_first_page = allow_empty_first_page
        self._num_pages = self._count = None

    def validate_number(self, number):
        "Validates the given 1-based page number."
        try:
            number = int(number)
        except ValueError:
            raise PageNotAnInteger('That page number is not an integer')
        if number < 1:
            raise EmptyPage('That page number is less than 1')

        if self.per_page == 1001:
            import pdb;pdb.set_trace()
        if number > self.num_pages:
            raise EmptyPage('That page contains no results')
        return number

    def page(self, number):
        "Returns a Page object for the given 1-based page number."
        number = self.validate_number(number)
        bottom = (number - 1) * self.per_page
        top = bottom + self.per_page
        if top + self.orphans >= self.count:
            top = self.count
        return Page(self.object_list[bottom:top], number, self)

    def _get_count(self):
        "Returns the total number of objects, across all pages."
        if self._count is None:
            try:
                self._count = self.object_list.count()
            except (AttributeError, TypeError):
                # AttributeError if object_list has no count() method.
                # TypeError if object_list.count() requires arguments
                # (i.e. is of type list).
                self._count = len(self.object_list)
        return self._count
    count = property(_get_count)

    def _get_num_pages(self):
        "Returns the total number of pages."
        if self._num_pages is None:
            if self.count == 0 and not self.allow_empty_first_page:
                self._num_pages = 0
            else:
                hits = max(1, self.count - self.orphans)
                self._num_pages = int(ceil(hits / float(self.per_page)))
        return self._num_pages
    num_pages = property(_get_num_pages)

    def _get_page_range(self):
        """
        Returns a 1-based range of pages for iterating through within
        a template for loop.
        """
        return range(1, self.num_pages + 1)
    page_range = property(_get_page_range)

class Page(object):
    def __init__(self, object_list, number, paginator):
        self.object_list = object_list
        self.number = number
        self.paginator = paginator

    def __repr__(self):
        return '<Page %s of %s>' % (self.number, self.paginator.num_pages)

    def has_next(self):
        return self.number < self.paginator.num_pages

    def has_previous(self):
        return self.number > 1

    def has_other_pages(self):
        return self.has_previous() or self.has_next()

    def next_page_number(self):
        return self.number + 1

    def previous_page_number(self):
        return self.number - 1

    def start_index(self):
        """
        Returns the 1-based index of the first object on this page,
        relative to total objects in the paginator.
        """
        # Special case, return zero if no items.
        if self.paginator.count == 0:
            return 0
        return (self.paginator.per_page * (self.number - 1)) + 1

    def end_index(self):
        """
        Returns the 1-based index of the last object on this page,
        relative to total objects found (hits).
        """
        # Special case for the last page because there can be orphans.
        if self.number == self.paginator.num_pages:
            return self.paginator.count
        return self.number * self.paginator.per_page
