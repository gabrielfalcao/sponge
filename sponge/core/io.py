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
import codecs
import fnmatch
import zipfile

from glob import glob
from os.path import abspath, join, dirname, curdir, exists

class FileSystem(object):
    stack = []

    def __init__(self):
        self.stack = []

    @classmethod
    def pushd(cls, path):
        if not len(cls.stack):
            cls.stack.append(cls.current_dir())

        cls.stack.append(path)
        os.chdir(path)

    @classmethod
    def popd(cls):
        if cls.stack:
            cls.stack.pop()
            if cls.stack:
                os.chdir(cls.stack[-1])

    @classmethod
    def filename(cls, path, with_extension=True):
        fname = os.path.split(path)[1]
        if not with_extension:
            fname = os.path.splitext(fname)[0]

        return fname

    @classmethod
    def dirname(cls, path):
        return dirname(path)

    @classmethod
    def exists(cls, path):
        return exists(path)

    @classmethod
    def mkdir(cls, path):
        try:
            os.makedirs(path)
        except OSError, e:
            # ignore if path already exists
            if e.errno not in (17, ):
                raise e
            else:
                if not os.path.isdir(path):
                    # but the path must be a dir to ignore its creation
                    raise e

    @classmethod
    def current_dir(cls, path=""):
        '''Returns the absolute path for current dir, also join the
        current path with the given, if so.'''
        to_return = cls.abspath(curdir)
        if path:
            return cls.join(to_return, path)

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
    def walk(cls, path):
        '''Walks through filesystem'''
        return os.walk(path)

    @classmethod
    def locate(cls, path, match, recursive=True):
        root_path = cls.abspath(path)
        if recursive:
            return_files = []
            for path, dirs, files in cls.walk(root_path):
                for filename in fnmatch.filter(files, match):
                    return_files.append(cls.join(path, filename))
            return return_files
        else:
            return glob(cls.join(root_path, match))

    @classmethod
    def extract_zip(cls, filename, base_path='.', verbose=False):
        base_path = cls.abspath(base_path)
        output = lambda x: verbose and sys.stdout.write("%s\n" % x)

        cls.pushd(base_path)
        zfile = zipfile.ZipFile(filename)

        output("Extracting files to %s" % base_path)
        for file_name in zfile.namelist():
            try:
                output("  -> Unpacking %s" % file_name)
                f = cls.open_raw(file_name, 'w')
                f.write(zfile.read(file_name))
                f.close()
            except IOError:
                output("---> Creating directory %s" % file_name)
                try:
                    cls.mkdir(file_name)
                except IOError, e:
                    pass
        cls.popd()

    @classmethod
    def open(cls, name, mode):
        path = name
        if not os.path.isabs(path):
            path = cls.current_dir(name)

        return codecs.open(path, mode, 'utf-8')

    @classmethod
    def open_raw(cls, name, mode):
        path = name
        if not os.path.isabs(path):
            path = cls.current_dir(name)

        return open(path, mode, 'utf-8')

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
        try:
            self.module = __import__(module_name)
        except ImportError:
            raise ImportError, \
                  'There is no module %s at %s' % (module_name,
                                                   dir_name)

        sys.path.pop()

    def load(self, classname):
        return getattr(self.module, classname)
