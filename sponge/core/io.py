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
import fnmatch

from glob import glob
from os.path import abspath, join, dirname, curdir

class FileSystem(object):

    def current_dir(self, path=""):
        '''Returns the absolute path for current dir, also join the
        current path with the given, if so.'''
        to_return = abspath(curdir)
        if path:
            return join(to_return, path)

        return to_return

    def abspath(self, path):
        '''Returns the absolute path for the given path.'''
        return abspath(path)

    def join(self, *args):
        '''Returns the concatenated path for the given arguments.'''
        return join(*args)

    def dirname(self, path):
        '''Returns the directory name for the given file.'''
        return dirname(path)

    def locate(self, path, match, recursive=True):
        root_path = self.abspath(path)

        if recursive:
            return_files = []
            for path, dirs, files in os.walk(root_path):
                for filename in fnmatch.filter(files, match):
                    return_files.append(self.join(path, filename))
            return return_files
        else:
            return glob(join(root_path, match))

class ClassLoader(object):
    def __init__(self, path):
        if not isinstance(path, basestring):
            raise TypeError, 'ClassLoader takes a string ' \
                  'as path parameter, got %s.' % repr(path)

        old_path = os.path.abspath(os.path.curdir)
        if not os.path.isdir(path):
            dir_name, file_name = os.path.split(path)
            module_name = os.path.splitext(file_name)[0]
            os.chdir(dir_name)
            self.module = __import__(module_name)
        else:
            dir_name, module_name = os.path.split(path.rstrip('/'))
            os.chdir(dir_name)
            self.module = __import__(module_name)

        os.chdir(old_path)

    def load(self, classname):
        return getattr(self.module, classname)
