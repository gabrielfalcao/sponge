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
from mox import Mox
from nose.tools import assert_equals
from utils import assert_raises

from sponge.core import ConfigParser, RequiredOptionError
from sponge.core import InvalidValueError

FULL_CONFIG_BASE = {
    'run-as': 'wsgi',
    'host': '0.0.0.0',
    'port': 80,
    'autoreload': False,
    'application': {
        'Controller': '/'
    },
    'databases': {
        'general': 'mysql://root@localhost/general'
    }
}

def assert_required_option(option, method, *args, **kw):
    p = r'You get to set "%s" option within settings.yml' % option
    assert_raises(RequiredOptionError, method, exc_pattern=p, *args, **kw)

def assert_invalid_option(option, value, method, *args, **kw):
    p = r'Invalid value in "%s" option: "%s". ' \
        'Read the Sponge documentation for more ' \
        'information.' % (option, value)

    assert_raises(InvalidValueError, method, exc_pattern=p, *args, **kw)

def test_config_parser_takes_dict():
    assert_raises(TypeError,
                  ConfigParser,
                  None,
                  exc_pattern=r'ConfigParser takes a dict as ' \
                  'parameter, got None.')

def test_config_parser_has_method_validate():
    assert hasattr(ConfigParser, 'validate'), \
           'ConfigParser should have the method validate'
    assert callable(ConfigParser.validate), \
           'ConfigParser.validate should be callable'

def test_config_parser_has_method_validate_mandatory():
    assert hasattr(ConfigParser, 'validate_mandatory'), \
           'ConfigParser should have the method validate_mandatory'
    assert callable(ConfigParser.validate_mandatory), \
           'ConfigParser.validate_mandatory should be callable'

def test_config_parser_has_method_validate_optional():
    assert hasattr(ConfigParser, 'validate_optional'), \
           'ConfigParser should have the method validate_optional'
    assert callable(ConfigParser.validate_optional), \
           'ConfigParser.validate_optional should be callable'

def test_config_parser_validate_calls_validation_methods():
    mocker = Mox()
    cp = ConfigParser({})
    cp.validate_mandatory = mocker.CreateMockAnything()
    cp.validate_optional = mocker.CreateMockAnything()

    cp.validate_mandatory()
    cp.validate_optional()

    mocker.ReplayAll()
    cp.validate()
    mocker.VerifyAll()

def test_has_method_raise_invalid():
    assert hasattr(ConfigParser, 'raise_invalid'), \
           'ConfigParser should have the method raise_invalid'
    assert callable(ConfigParser.raise_invalid), \
           'ConfigParser.raise_invalid should be callable'

def test_raise_invalid_raises():
    cp = ConfigParser({})
    assert_invalid_option('foo-bar', 'john-doe',
                          cp.raise_invalid, 'foo-bar', 'john-doe')

def test_validate_mandatory_requires_option_run_as():
    d = FULL_CONFIG_BASE.copy()
    del d['run-as']
    cp = ConfigParser(d)
    assert_required_option('run-as', cp.validate_mandatory)

def test_invalid_mandatory_option_run_as():
    d = FULL_CONFIG_BASE.copy()
    d['run-as'] = 'blabla'
    cp = ConfigParser(d)
    assert_invalid_option('run-as', 'blabla', cp.validate_mandatory)

def test_validate_mandatory_option_run_as_wsgi():
    d = FULL_CONFIG_BASE.copy()
    d['run-as'] = 'wsgi'
    cp = ConfigParser(d)
    assert cp.validate_mandatory()

def test_validate_mandatory_option_run_as_standalone():
    d = FULL_CONFIG_BASE.copy()
    d['run-as'] = 'standalone'
    cp = ConfigParser(d)
    assert cp.validate_mandatory()

def test_validate_mandatory_requires_option_host():
    d = FULL_CONFIG_BASE.copy()
    del d['host']
    cp = ConfigParser(d)
    assert_required_option('host', cp.validate_mandatory)

def test_invalid_mandatory_option_host():
    d = FULL_CONFIG_BASE.copy()
    d['host'] = 'invalid_host_string'
    cp = ConfigParser(d)
    assert_invalid_option('host', 'invalid_host_string',
                          cp.validate_mandatory)

def test_validate_option_host():
    d = FULL_CONFIG_BASE.copy()
    d['host'] = '127.0.0.1'
    cp = ConfigParser(d)
    assert cp.validate_mandatory()

def test_validate_mandatory_requires_option_port():
    d = FULL_CONFIG_BASE.copy()
    del d['port']
    cp = ConfigParser(d)
    assert_required_option('port', cp.validate_mandatory)

def test_invalid_mandatory_option_port_float():
    d = FULL_CONFIG_BASE.copy()
    d['port'] = 90.2
    cp = ConfigParser(d)
    assert_invalid_option('port', '90.2',
                          cp.validate_mandatory)

def test_invalid_mandatory_option_port_string():
    d = FULL_CONFIG_BASE.copy()
    d['port'] = 'invalid_port'
    cp = ConfigParser(d)
    assert_invalid_option('port', 'invalid_port',
                          cp.validate_mandatory)

def test_validate_option_port():
    d = FULL_CONFIG_BASE.copy()
    d['port'] = '8080'
    cp = ConfigParser(d)
    assert cp.validate_mandatory()

