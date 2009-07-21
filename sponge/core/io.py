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

import os
import sys
import fnmatch

from glob import glob
from os.path import abspath, join, dirname, curdir

class FileSystem(object):
    @classmethod
    def current_dir(cls, path=""):
        '''Returns the absolute path for current dir, also join the
        current path with the given, if so.'''
        to_return = abspath(curdir)
        if path:
            return join(to_return, path)

        return to_return

    @classmethod
    def abspath(cls, path):
        '''Returns the absolute path for the given path.'''
        return abspath(path)

    @classmethod
    def join(cls, *args):
        '''Returns the concatenated path for the given arguments.'''
        return join(*args)

    @classmethod
    def dirname(cls, path):
        '''Returns the directory name for the given file.'''
        return dirname(path)

    @classmethod
    def locate(cls, path, match, recursive=True):
        root_path = cls.abspath(path)

        if recursive:
            return_files = []
            for path, dirs, files in os.walk(root_path):
                for filename in fnmatch.filter(files, match):
                    return_files.append(cls.join(path, filename))
            return return_files
        else:
            return glob(join(root_path, match))

class ClassLoader(object):
    def __init__(self, path):
        if not isinstance(path, basestring):
            raise TypeError, 'ClassLoader takes a string ' \
                  'as path parameter, got %s.' % repr(path)

        if not os.path.isdir(path):
            dir_name, file_name = os.path.split(path)
            module_name = os.path.splitext(file_name)[0]
        else:
            dir_name, module_name = os.path.split(path.rstrip('/'))

        sys.path.append(dir_name)
        self.module = __import__(module_name)

        sys.path.pop()

    def load(self, classname):
        return getattr(self.module, classname)
