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
import cherrypy

def route(route, name=None):
    def dec(func):
        conf = (
            name, {
                'route': route,
                'method': func.__name__
            }
        )
        return func, conf

    return dec

class MetaController(type):
    def __init__(cls, name, bases, attrs):
        if name not in ('MetaController', 'Controller'):
            cls.__routes__ = []
            for attr, value in attrs.items():
                if isinstance(value, tuple) and len(value) is 2:
                    method, conf = value
                    setattr(cls, attr, method)
                    cls.__routes__.append(conf)

        super(MetaController, cls).__init__(name, bases, attrs)

class Controller(object):
    __metaclass__ = MetaController
    __routes__ = None
