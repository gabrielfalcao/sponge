#!/usr/bin/env python
# -*- coding: utf-8 -*-
# <Sponge - Lightweight Web Framework>
# Copyright (C) 2009 Gabriel Falcão <gabriel@nacaolivre.org>
# Copyright (C) 2009 Bernardo Heynemann <heynemann@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re
import cherrypy

from cherrypy.lib import static

from sponge.core.io import FileSystem
from sponge.helpers.image import jpeg, picture

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
                return static.serve_file(cache_full_path, 'image/jpeg')

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
