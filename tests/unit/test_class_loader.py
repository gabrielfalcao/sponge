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

from re import escape
from mox import Mox
from nose.tools import assert_equals
from utils import assert_raises

from sponge.core import io

def test_class_loader_takes_a_string_path_raises_with_number():
    assert_raises(TypeError, io.ClassLoader, 5,
                  exc_pattern=r'ClassLoader takes a string ' \
                  'as path parameter, got 5.')

def test_class_loader_takes_a_string_path_raises_with_none():
    assert_raises(TypeError, io.ClassLoader, None,
                  exc_pattern=r'ClassLoader takes a string ' \
                  'as path parameter, got None.')

def test_class_loader_loads_from_file():
    mox = Mox()

    mox.StubOutWithMock(io, 'os')
    import_func = __import__
    io.__import__ = mox.CreateMockAnything()

    class_dir = '/full/path/to/module/or'
    class_file = 'file.py'
    class_path = '%s/%s' % (class_dir, class_file)

    io.os.path = mox.CreateMockAnything()
    io.os.path.curdir = "."
    io.os.path.abspath(".").AndReturn('should_be_old_abspath')

    io.os.path.isdir(class_path).AndReturn(False)

    io.os.path.split(class_path).AndReturn((class_dir, class_file))
    io.os.path.splitext(class_file).AndReturn(('file', '.py'))

    io.os.chdir(class_dir)

    module_mock = mox.CreateMockAnything()
    module_mock.ClassIWantToLoad = 'should_be_expected_class'
    io.__import__('file').AndReturn(module_mock)
    io.os.chdir('should_be_old_abspath')

    mox.ReplayAll()

    try:
        cl = io.ClassLoader(class_path)
        assert_equals(cl.load('ClassIWantToLoad'), 'should_be_expected_class')
        mox.VerifyAll()
    finally:
        mox.UnsetStubs()
