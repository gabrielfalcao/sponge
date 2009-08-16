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

from sponge.core import ConfigValidator, RequiredOptionError
from sponge.core import InvalidValueError

FULL_CONFIG_BASE = {
    'run-as': 'wsgi',
    'host': '0.0.0.0',
    'port': 80,
    'autoreload': False,
    'application': {
        'classes': {
            'SomeController': '/'
        },
        'image-dir': '/home/user/projects/web-app/images',
        'path': '/home/user/projects/web-app/module',
        'template-dir': '/home/user/projects/web-app/html'
    },
    'static': {
        '/media': '/home/user/projects/web-app/static',
    },
    'databases': {
        'general': 'mysql://root@localhost/general'
    }
}

def test_assert_has_inner_class_anyvalue():
    assert hasattr(ConfigValidator, 'AnyValue'), \
           'ConfigValidator should have attribute AnyValue'
    assert isinstance(ConfigValidator.AnyValue, type), \
           'ConfigValidator.AnyValue should be a class'

def test_assert_any_value_takes_type():
    assert_raises(TypeError, ConfigValidator.AnyValue, '',
                  exc_pattern=r'ConfigValidator.AnyValue takes a ' \
                  'type as parameter, got \'\'')

def test_any_value_stashes_vartype():
    av = ConfigValidator.AnyValue(bool)
    assert_equals(av.vartype, bool)

def assert_required_option(option, method, *args, **kw):
    p = r'You get to set "%s" option within settings.yml' % escape(option)
    assert_raises(RequiredOptionError, method, exc_pattern=p, *args, **kw)

def assert_invalid_option(option, value, method, *args, **kw):
    if isinstance(value, basestring):
        value = escape(value)
    else:
        value = repr(value)

    p = r'Invalid value in "%s" option: "%s". ' \
        'Read the Sponge documentation for more ' \
        'information.' % (escape(option), value)

    assert_raises(InvalidValueError, method, exc_pattern=p, *args, **kw)

def test_config_validator_takes_dict():
    assert_raises(TypeError,
                  ConfigValidator,
                  None,
                  exc_pattern=r'ConfigValidator takes a dict as ' \
                  'parameter, got None.')

def test_config_validator_has_method_validate():
    assert hasattr(ConfigValidator, 'validate'), \
           'ConfigValidator should have the method validate'
    assert callable(ConfigValidator.validate), \
           'ConfigValidator.validate should be callable'

def test_config_validator_has_method_validate_mandatory():
    assert hasattr(ConfigValidator, 'validate_mandatory'), \
           'ConfigValidator should have the method validate_mandatory'
    assert callable(ConfigValidator.validate_mandatory), \
           'ConfigValidator.validate_mandatory should be callable'

def test_config_validator_validate_calls_validation_methods():
    mocker = Mox()
    cp = ConfigValidator({})
    cp.validate_mandatory = mocker.CreateMockAnything()
    cp.validate_optional = mocker.CreateMockAnything()

    cp.validate_mandatory()

    mocker.ReplayAll()
    cp.validate()
    mocker.VerifyAll()

def test_has_method_raise_invalid():
    assert hasattr(ConfigValidator, 'raise_invalid'), \
           'ConfigValidator should have the method raise_invalid'
    assert callable(ConfigValidator.raise_invalid), \
           'ConfigValidator.raise_invalid should be callable'

def test_raise_invalid_raises():
    cp = ConfigValidator({})
    assert_invalid_option('foo-bar', 'john-doe',
                          cp.raise_invalid, 'foo-bar', 'john-doe')

def test_validate_mandatory_requires_option_run_as():
    d = FULL_CONFIG_BASE.copy()
    del d['run-as']
    cp = ConfigValidator(d)
    assert_required_option('run-as', cp.validate_mandatory)

def test_invalid_mandatory_option_run_as():
    d = FULL_CONFIG_BASE.copy()
    d['run-as'] = 'blabla'
    cp = ConfigValidator(d)
    assert_invalid_option('run-as', 'blabla', cp.validate_mandatory)

def test_validate_mandatory_option_run_as_wsgi():
    d = FULL_CONFIG_BASE.copy()
    d['run-as'] = 'wsgi'
    cp = ConfigValidator(d)
    assert cp.validate_mandatory()

def test_validate_mandatory_option_run_as_standalone():
    d = FULL_CONFIG_BASE.copy()
    d['run-as'] = 'standalone'
    cp = ConfigValidator(d)
    assert cp.validate_mandatory()

def test_validate_mandatory_requires_option_host():
    d = FULL_CONFIG_BASE.copy()
    del d['host']
    cp = ConfigValidator(d)
    assert_required_option('host', cp.validate_mandatory)

def test_invalid_mandatory_option_host():
    d = FULL_CONFIG_BASE.copy()
    d['host'] = 'invalid_host_string'
    cp = ConfigValidator(d)
    assert_invalid_option('host', 'invalid_host_string',
                          cp.validate_mandatory)

def test_validate_option_host():
    d = FULL_CONFIG_BASE.copy()
    d['host'] = '127.0.0.1'
    cp = ConfigValidator(d)
    assert cp.validate_mandatory()

def test_validate_mandatory_requires_option_port():
    d = FULL_CONFIG_BASE.copy()
    del d['port']
    cp = ConfigValidator(d)
    assert_required_option('port', cp.validate_mandatory)

def test_invalid_mandatory_option_port_float():
    d = FULL_CONFIG_BASE.copy()
    d['port'] = 90.2
    cp = ConfigValidator(d)
    assert_invalid_option('port', '90.2',
                          cp.validate_mandatory)

def test_invalid_mandatory_option_port_string():
    d = FULL_CONFIG_BASE.copy()
    d['port'] = 'invalid_port'
    cp = ConfigValidator(d)
    assert_invalid_option('port', 'invalid_port',
                          cp.validate_mandatory)

def test_validate_option_port():
    d = FULL_CONFIG_BASE.copy()
    d['port'] = '8080'
    cp = ConfigValidator(d)
    assert cp.validate_mandatory()

def test_validate_mandatory_requires_option_autoreload():
    d = FULL_CONFIG_BASE.copy()
    del d['autoreload']
    cp = ConfigValidator(d)
    assert_required_option('autoreload', cp.validate_mandatory)

def test_invalid_mandatory_option_autoreload_string():
    d = FULL_CONFIG_BASE.copy()
    d['autoreload'] = 'should_be_bool'
    cp = ConfigValidator(d)
    assert_invalid_option('autoreload', 'should_be_bool',
                          cp.validate_mandatory)

def test_validate_option_autoreload():
    d = FULL_CONFIG_BASE.copy()
    d['autoreload'] = True
    cp = ConfigValidator(d)
    assert cp.validate_mandatory()

def test_validate_mandatory_requires_option_application():
    d = FULL_CONFIG_BASE.copy()
    del d['application']
    cp = ConfigValidator(d)
    assert_required_option('application', cp.validate_mandatory)

def test_invalid_mandatory_option_application_string():
    d = FULL_CONFIG_BASE.copy()
    d['application'] = 'should_be_dict'
    cp = ConfigValidator(d)
    assert_invalid_option('application', 'should_be_dict',
                          cp.validate_mandatory)

def test_invalid_mandatory_option_application_none():
    d = FULL_CONFIG_BASE.copy()
    d['application'] = None
    cp = ConfigValidator(d)
    assert_invalid_option('application', None,
                          cp.validate_mandatory)

def test_application_invalid_controller_name_numeral():
    d = FULL_CONFIG_BASE.copy()
    d['application'] = {
        'classes':{
            '5NumeralController': '/',
        }
    }

    cp = ConfigValidator(d)
    assert_invalid_option('classes', '5NumeralController',
                          cp.validate_mandatory)

def test_application_invalid_controller_name_bad_characters():
    d = FULL_CONFIG_BASE.copy()
    d['application'] = {
        'classes':{
            '-040%$WeirdNameController': '/',
        }
    }

    cp = ConfigValidator(d)
    assert_invalid_option('classes', '-040%$WeirdNameController',
                          cp.validate_mandatory)

def test_application_invalid_controller_name_spaces():
    d = FULL_CONFIG_BASE.copy()
    d['application'] = {
        'classes':{
            'Controller With Spaces': '/',
        }
    }

    cp = ConfigValidator(d)
    assert_invalid_option('classes', 'Controller With Spaces',
                          cp.validate_mandatory)

def test_controller_url_should_start_with_slash():
    d = FULL_CONFIG_BASE.copy()
    d['application'] = {
        'classes':{
            'Controller With Spaces': 'wee/',
        }
    }

    cp = ConfigValidator(d)
    assert_invalid_option('classes', 'Controller With Spaces',
                          cp.validate_mandatory)

def test_application_invalid_names_with_spaces():
    d = FULL_CONFIG_BASE.copy()
    d['application'] = {
        'path with spaces': '/',
    }

    cp = ConfigValidator(d)
    assert_invalid_option('application', 'path with spaces',
                          cp.validate_mandatory)

def test_application_invalid_names_with_bad_characters():
    d = FULL_CONFIG_BASE.copy()
    d['application'] = {
        'fjkdas#@$%*kdfhagf': '/',
    }

    cp = ConfigValidator(d)
    assert_invalid_option('application', 'fjkdas#@$%*kdfhagf',
                          cp.validate_mandatory)

def test_application_invalid_names_starting_with_number():
    d = FULL_CONFIG_BASE.copy()
    d['application'] = {
        '3kdjfbsff': '/',
    }

    cp = ConfigValidator(d)
    assert_invalid_option('application', '3kdjfbsff',
                          cp.validate_mandatory)

def test_application_invalid_values_without_bar_at_start():
    d = FULL_CONFIG_BASE.copy()
    d['application'] = {
        'something': 'asd/',
    }

    cp = ConfigValidator(d)
    assert_invalid_option('something', 'asd/',
                          cp.validate_mandatory)

def test_validate_option_application():
    d = FULL_CONFIG_BASE.copy()
    d['application'] = {
        'image-dir': '/home/user/projects/web-app/images',
        'path': '/home/user/projects/web-app/module',
        'template-dir': '/home/user/projects/web-app/html',
        'classes':{
            'RootController': '/',
            'WikiController': '/wiki',
            'MediaController': '/media',
        }
    }
    cp = ConfigValidator(d)
    assert cp.validate_mandatory()

def test_validate_sub_options_should_be_dict():
    d = FULL_CONFIG_BASE.copy()
    d['databases'] = {
        'classes': 213
    }
    cp = ConfigValidator(d)
    assert_invalid_option('classes', '213',
                          cp.validate_mandatory)

def test_validate_mandatory_does_not_require_option_databases():
    d = FULL_CONFIG_BASE.copy()
    del d['databases']
    cp = ConfigValidator(d)
    cp.validate_mandatory()

def test_invalid_mandatory_option_databases_string():
    d = FULL_CONFIG_BASE.copy()
    d['databases'] = 'should_be_dict'
    cp = ConfigValidator(d)
    assert_invalid_option('databases', 'should_be_dict',
                          cp.validate_mandatory)

def test_invalid_mandatory_option_databases_none():
    d = FULL_CONFIG_BASE.copy()
    d['databases'] = None
    cp = ConfigValidator(d)
    assert_invalid_option('databases', None,
                          cp.validate_mandatory)

def test_databases_invalid_controller_name_weird_charactes():
    d = FULL_CONFIG_BASE.copy()
    d['databases'] = {
        '%$*': 'sqlite://asdasd',
    }

    cp = ConfigValidator(d)
    assert_invalid_option('databases', '%$*',
                          cp.validate_mandatory)

def test_validate_mandatory_does_not_requires_option_static():
    d = FULL_CONFIG_BASE.copy()
    del d['static']
    cp = ConfigValidator(d)
    cp.validate_mandatory()

def test_invalid_mandatory_option_static_int():
    d = FULL_CONFIG_BASE.copy()
    d['static'] = 10
    cp = ConfigValidator(d)
    assert_invalid_option('static', '10',
                          cp.validate_mandatory)

def test_invalid_mandatory_option_static_none():
    d = FULL_CONFIG_BASE.copy()
    d['static'] = None
    cp = ConfigValidator(d)
    assert_invalid_option('static', 'None',
                          cp.validate_mandatory)

def test_invalid_mandatory_option_static_string():
    d = FULL_CONFIG_BASE.copy()
    d['static'] = 'should_be_dict'
    cp = ConfigValidator(d)
    assert_invalid_option('static', 'should_be_dict',
                          cp.validate_mandatory)

def test_static_invalid_controller_name_weird_charactes():
    d = FULL_CONFIG_BASE.copy()
    d['static'] = {
        '%$*': 'sqlite://asdasd',
    }

    cp = ConfigValidator(d)
    assert_invalid_option('static', '%$*',
                          cp.validate_mandatory)
