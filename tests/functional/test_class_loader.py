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
from os.path import split, join
from nose.tools import assert_equals
from sponge.core.io import ClassLoader, FileSystem

def test_load_module():
    this_path = split(__file__)[0]
    relative_path = join(this_path, 'module', 'to', 'load')
    module_path = FileSystem.current_dir(relative_path)
    ClassToLoad = ClassLoader(module_path).load('ClassInsideModule')

    assert_equals(ClassToLoad.__name__, 'ClassInsideModule')
    assert hasattr(ClassToLoad, 'param'), \
           '%r should have the attribute "param"' % ClassToLoad
    assert_equals(ClassToLoad.param, 'ParamFromClass')

def test_load_file():
    this_path = split(__file__)[0]
    relative_path = join(this_path, 'module', 'to', 'load', 'some_file.py')
    module_path = FileSystem.current_dir(relative_path)
    ClassToLoad = ClassLoader(module_path).load('ClassInsideFile')

    assert_equals(ClassToLoad.__name__, 'ClassInsideFile')
    assert hasattr(ClassToLoad, 'param'), \
           '%r should have the attribute "param"' % ClassToLoad
    assert_equals(ClassToLoad.param, 'ParamFromClass')
