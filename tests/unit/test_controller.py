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
import cherrypy

from mox import Mox
from nose.tools import assert_equal
from utils import assert_raises
from sponge import controller

def test_route_return_tuple():
    @controller.route('route_name', 'route/:foo/other/:bar')
    def my_func():
        return 'it is my func'

    assert isinstance(my_func, tuple), 'A function decorated with ' \
           'route should be a tuple'
    assert len(my_func) == 2, 'the tuple should have two items'
    assert callable(my_func[0]), 'first item of tuple should be the actual callable'
    assert isinstance(my_func[1], tuple)

def test_controller_with_route_named():
    class MyController(controller.Controller):
        @controller.route('/path/:to/:route/:param3', name='my_route_name')
        def some_method(self, to, route, param3):
            return 'something'

    assert hasattr(MyController, '__routes__'), 'MyController should have __routes__'
    assert_equal(MyController.__routes__, [
        ('my_route_name', {
            'route': '/path/:to/:route/:param3',
            'method': 'some_method'
        }),
    ])

def test_controller_with_route_without_name():
    class MyController(controller.Controller):
        @controller.route('/path/:to/:route/:param3')
        def some_method(self, to, route, param3):
            return 'something'

    assert hasattr(MyController, '__routes__'), 'MyController should have __routes__'
    assert_equal(MyController.__routes__, [
        (None, {
            'route': '/path/:to/:route/:param3',
            'method': 'some_method'
        }),
    ])
