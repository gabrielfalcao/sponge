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

class InvalidValueError(Exception):
    pass

class RequiredOptionError(Exception):
    pass

class AnyValue(object):
    pass

class ConfigParser(object):
    mandatory = {
        'run-as': ['standalone', 'wsgi'],
        'host': r'^\d{1,3}[.]\d{1,3}[.]\d{1,3}[.]\d{1,3}$',
        'port': r'^\d+$',
        'autoreload': AnyValue,
        'application': {
            r'^[a-zA-Z]\w*': r'[/].*$'
        },
        'databases': {
            r'^\w+$': '.+'
        }
    }
    def __init__(self, cdict):
        if not isinstance(cdict, dict):
            raise TypeError, 'ConfigParser takes a dict as parameter, got None.'
        self.cdict = cdict

    def validate(self):
        self.validate_mandatory()
        self.validate_optional()

    def validate_mandatory(self):
        keys = self.cdict.keys()
        for option in self.mandatory:
            if option not in keys:
                raise RequiredOptionError, \
                      'You get to set "%s" option within settings.yml' % option
            validator = self.mandatory[option]
            value = unicode(self.cdict[option])
            if isinstance(validator, list):
                if value not in validator:
                    raise InvalidValueError, 'Invalid value in "%s" ' \
                          'option: "%s". Read the Sponge documentation ' \
                          'for more information.' % (option, value)
            if isinstance(validator, basestring):
                if not re.match(validator, value):
                    raise InvalidValueError, 'Invalid value in "%s" ' \
                          'option: "%s". Read the Sponge documentation ' \
                          'for more information.' % (option, value)

        return True

    def validate_optional(self):
        pass

