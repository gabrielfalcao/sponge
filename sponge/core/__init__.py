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


class ConfigValidator(object):
    class AnyValue(object):
        def __init__(self, vartype):
            if not isinstance(vartype, type):
                raise TypeError, 'ConfigValidator.AnyValue takes a ' \
                  'type as parameter, got %s' % repr(vartype)
            self.vartype = vartype

    mandatory = {
        'run-as': ['standalone', 'wsgi'],
        'host': r'^\d{1,3}[.]\d{1,3}[.]\d{1,3}[.]\d{1,3}$',
        'port': r'^\d+$',
        'autoreload': AnyValue(bool),
        'application': {
            r'^[a-zA-Z_-][\w_-]*$': r'^[/].*$'
        },
        'static': {
            r'^[a-zA-Z/_-][\w_-]*$': r'^[/].*$'
        },
        'databases': {
            r'^[\w_-]+$': '^.+$'
        }
    }
    def __init__(self, cdict):
        if not isinstance(cdict, dict):
            raise TypeError, 'ConfigValidator takes a dict as parameter, got None.'
        self.cdict = cdict

    def validate(self):
        self.validate_mandatory()
        self.validate_optional()

    def raise_invalid(self, option, value):
        raise InvalidValueError, 'Invalid value in "%s" ' \
              'option: "%s". Read the Sponge documentation ' \
              'for more information.' % (option, value)

    def validate_mandatory(self):
        keys = self.cdict.keys()
        for option in self.mandatory:
            if option not in keys:
                raise RequiredOptionError, \
                      'You get to set "%s" option within settings.yml' % option
            validator = self.mandatory[option]
            raw_value = self.cdict[option]
            value = unicode(raw_value)
            if isinstance(validator, list):
                if value not in validator:
                    self.raise_invalid(option, value)

            if isinstance(validator, basestring):
                if not re.match(validator, value):
                    self.raise_invalid(option, value)

            if isinstance(validator, self.AnyValue):
                if not isinstance(raw_value, validator.vartype):
                    self.raise_invalid(option, value)

            if isinstance(validator, dict):
                if not isinstance(raw_value, dict):
                    self.raise_invalid(option, value)
                self.validate_dict(option, validator, raw_value)

        return True

    def validate_optional(self):
        pass

    def validate_dict(self, option, validator, dict_to_validate):
        for key_regex, value_regex in validator.items():
            for key, value in dict_to_validate.items():
                if isinstance(value, dict):
                    self.validate_dict(key, validator, value)

                elif isinstance(value, basestring):
                    if not re.match(key_regex, key):
                        self.raise_invalid(option, key)
                    if not re.match(value_regex, value):
                        self.raise_invalid(key, value)

                else:
                    self.raise_invalid(key, value)
