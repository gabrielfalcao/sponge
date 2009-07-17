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

from sponge.core.io import SettingsLoader

def test_settings_loader_takes_a_string_path_raises_with_number():
    assert_raises(TypeError, SettingsLoader, 5,
                  exc_pattern=r'SettingsLoader takes a string ' \
                  'as path parameter, got 5.')

def test_settings_loader_takes_a_string_path_raises_with_none():
    assert_raises(TypeError, SettingsLoader, None,
                  exc_pattern=r'SettingsLoader takes a string ' \
                  'as path parameter, got None.')
