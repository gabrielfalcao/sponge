#!/usr/bin/env python
# -*- coding: utf-8; -*-
#
# Copyright (C) 2009 Gabriel Falcão <gabriel@nacaolivre.org>
# Copyright (C) 2009 Bernardo Heynemann <heynemann@gmail.com>
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

import sys
import yaml
import cherrypy
import optparse

from os.path import abspath, join, dirname
from mox import Mox
from nose.tools import assert_equals
from utils import assert_raises

from sponge import bob
from StringIO import StringIO

basic_config = {
    'run-as': 'wsgi',
    'host': '0.0.0.0',
    'port': 4000,
    'autoreload': True,
    'application': {
        'classes': {
            'HelloWorldController': '/',
            'AjaxController': '/ajax',
        },
        'image-dir': None,
        'path': None,
        'template-dir': None,
        'static': {
            '/media': None,
        },
    },
}

def test_can_create_bob():
    b = bob.Bob()
    assert b
    assert isinstance(b, bob.Bob)

def test_run_fails_with_unknown_args():
    mox = Mox()

    mock_parser = mox.CreateMockAnything()
    mock_parser.parse_args().AndReturn(("options", ["args"]))

    mox.ReplayAll()

    b = bob.Bob(parser=mock_parser)
    sys.stderr = StringIO()
    assert_raises(SystemExit, b.run)
    assert_equals(sys.stderr.getvalue(),
                  '\nargs is an invalid argument, choose one ' \
                  'in create, go, start\n')
    sys.stderr = sys.__stderr__
    mox.VerifyAll()

def test_run_fails_without_args():
    mox = Mox()

    mock_parser = mox.CreateMockAnything()
    mock_parser.parse_args().AndReturn(("options", []))

    mox.ReplayAll()

    b = bob.Bob(parser=mock_parser)
    sys.stderr = StringIO()
    assert_raises(SystemExit, b.run)
    assert_equals(sys.stderr.getvalue(),
                  '\nmissing argument, choose one ' \
                  'in create, go, start\n')
    sys.stderr = sys.__stderr__
    mox.VerifyAll()

def test_run_calls_create_with_second_argument():
    mox = Mox()

    mock_parser = mox.CreateMockAnything()
    mock_parser.parse_args().AndReturn(("options", ['create', 'some']))
    b = bob.Bob(parser=mock_parser)
    b.create = mox.CreateMockAnything()
    b.create('some')

    mox.ReplayAll()
    b.run()
    mox.VerifyAll()

def test_run_calls_go():
    mox = Mox()

    mock_parser = mox.CreateMockAnything()
    mock_parser.parse_args().AndReturn(("options", ['go']))
    b = bob.Bob(parser=mock_parser)
    b.go = mox.CreateMockAnything()
    b.go()

    mox.ReplayAll()
    b.run()
    mox.VerifyAll()

def test_run_calls_start_with_second_argument():
    mox = Mox()

    mock_parser = mox.CreateMockAnything()
    mock_parser.parse_args().AndReturn(("options", ['start', 'some']))
    b = bob.Bob(parser=mock_parser)
    b.start = mox.CreateMockAnything()
    b.start('some')

    mox.ReplayAll()
    b.run()
    mox.VerifyAll()

def test_go_through_main_run():
    mox = Mox()
    bobby = bob.Bob
    old_sys = bob.sys

    mock_parser = mox.CreateMockAnything()
    file_system = mox.CreateMockAnything()

    bob.sys = mox.CreateMockAnything()

    bob_mock = mox.CreateMockAnything()
    bob_instance_mock = mox.CreateMockAnything()
    bob_instance_mock.run = mox.CreateMockAnything()

    bob_instance_mock.run().AndReturn(0)
    bob_mock.__call__(parser=mock_parser, fs=file_system).AndReturn(bob_instance_mock)
    bob.sys.exit(0)
    bob.Bob = bob_mock
    mox.ReplayAll()

    try:
        got = bob.run(parser=mock_parser, fs=file_system)
        mox.VerifyAll()
    finally:
        mox.UnsetStubs()
        bob.Bob = bobby
        bob.sys = old_sys

def test_exit_without_args():
    mox = Mox()
    mock_parser = mox.CreateMockAnything()

    b = bob.Bob(parser=mock_parser)
    assert_raises(SystemExit, b.exit, exc_pattern=r'1')

def test_exit_with_specific_exit_code():
    mox = Mox()
    mock_parser = mox.CreateMockAnything()

    b = bob.Bob(parser=mock_parser)
    assert_raises(SystemExit, b.exit, 100, exc_pattern=r'100')

def test_configure():
    mox = Mox()
    mock_parser = mox.CreateMockAnything()

    mox.StubOutWithMock(bob, 'yaml')
    config_validator = bob.ConfigValidator
    sponge_config = bob.SpongeConfig

    bob.ConfigValidator = mox.CreateMockAnything()
    bob.SpongeConfig = mox.CreateMockAnything()

    b = bob.Bob(parser=mock_parser)
    b.fs = mox.CreateMockAnything()

    b.fs.current_dir().AndReturn('should_be_current_dir')
    b.fs.current_dir('settings.yml'). \
         AndReturn('/current/path/settings-yaml')

    file_mock = mox.CreateMockAnything()
    b.fs.open('/current/path/settings-yaml', 'r'). \
         AndReturn(file_mock)

    file_mock.read().AndReturn('should-be-raw-yaml-text')
    bob.yaml.load('should-be-raw-yaml-text'). \
        AndReturn('should-be-config-dict')

    bob.ConfigValidator('should-be-config-dict'). \
        AndReturn('should-be-validator')

    config_mock = mox.CreateMockAnything()
    bob.SpongeConfig(cherrypy.config, 'should-be-validator'). \
        AndReturn(config_mock)

    config_mock.setup_all('should_be_current_dir')

    mox.ReplayAll()
    try:
        b.configure()
        mox.VerifyAll()
    finally:
        mox.UnsetStubs()
        bob.ConfigValidator = config_validator
        bob.SpongeConfig = sponge_config

def test_go():
    mox = Mox()
    mox.StubOutWithMock(bob, 'cherrypy')

    b = bob.Bob()
    b.configure = mox.CreateMockAnything()
    b.configure()
    bob.cherrypy.quickstart()
    mox.ReplayAll()
    try:
        b.go()
        mox.VerifyAll()
    finally:
        mox.UnsetStubs()

def test_create_fails_without_argument():
    b = bob.Bob()
    sys.stderr = StringIO()
    assert_raises(SystemExit, b.create, None)
    assert_equals(sys.stderr.getvalue(),
                  '\nmissing project name, try something like ' \
                  '"bob create foobar"\n')
    sys.stderr = sys.__stderr__

def test_create_fails_if_path_already_exists():
    mox = Mox()
    b = bob.Bob()
    b.fs = mox.CreateMockAnything()

    b.fs.current_dir('my-project'). \
         AndReturn('/full/path/to/my-project')

    b.fs.exists('/full/path/to/my-project'). \
         AndReturn(True)

    mox.ReplayAll()
    try:
        sys.stderr = StringIO()
        assert_raises(SystemExit, b.create, 'my-project')
        assert_equals(sys.stderr.getvalue(),
                      '\nThe path "/full/path/to/my-project" ' \
                      'already exists. Maybe you could choose ' \
                      'another name for your project ?\n')
    finally:
        sys.stderr = sys.__stderr__

def test_create_success():
    mox = Mox()
    b = bob.Bob()
    b.fs = mox.CreateMockAnything()
    b.fs.join = join

    mox.StubOutWithMock(bob, 'SpongeData')
    mox.StubOutWithMock(bob, 'yaml')

    full_path = '/full/path/to/my-project'
    b.fs.current_dir('my-project'). \
         AndReturn(full_path)

    b.fs.exists(full_path). \
         AndReturn(False)

    b.fs.mkdir(full_path)

    file_mock = mox.CreateMockAnything()
    b.fs.open(join(full_path, 'settings.yml'), 'w'). \
         AndReturn(file_mock)

    expected_dict = basic_config.copy()
    expected_dict['application'].update({
        'static': {
            '/media': join('media')
        },
        'path': join('app', 'controllers.py'),
        'image-dir': join('media', 'img'),
        'template-dir': join('templates'),
    })

    bob.yaml.dump(expected_dict, indent=True).AndReturn('should-be-a-yaml')
    file_mock.write('should-be-a-yaml')
    file_mock.close()

    bob.SpongeData.get_file('project.zip'). \
        AndReturn('should-be-path-to-zip-file')

    b.fs.extract_zip('should-be-path-to-zip-file', full_path)

    mox.ReplayAll()
    b.create('my-project')
    mox.VerifyAll()

def test_start():
    mox = Mox()
    b = bob.Bob()
    b.fs = mox.CreateMockAnything()
    b.create = mox.CreateMockAnything()
    b.go = mox.CreateMockAnything()

    b.create('foo-bar')
    b.fs.pushd('foo-bar')
    b.go()

    mox.ReplayAll()

    b.start('foo-bar')

    mox.VerifyAll()

def test_fix_yml():
    expected = """
test:
  with:
    Items: here
    And: Here
"""
    wrong = """
test:
  with: {Items: here, And: Here}
"""

    b = bob.Bob()

    got = b.fix_yml(wrong)

    assert_equals(got, expected)

def test_bob_help():
    b = bob.Bob()
    assert_equals(b.get_help(), "\n Sponge Bob is the responsible for " \
                  "managing\n    the user's application and its modules. " \
                  "\n\nTo use type %prog [options] or %prog -h (--help) " \
                  "for help with the available options\n\nACTIONS:\n\ncreate " \
                  "<projectname> - creates a new project, which means " \
                  "creating a new folder in current directory, named " \
                  "projectname\ngo start the cherrypy server using the " \
                  "configuration file settings.yml in current directory." \
                  "\nstart <projectname> executes both bob create and bob go")
