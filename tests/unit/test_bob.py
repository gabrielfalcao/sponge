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
                  'in create, go, test, start\n')
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
                  'in create, go, test, start\n')
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

def test_run_calls_test():
    mox = Mox()

    mock_parser = mox.CreateMockAnything()
    mock_parser.parse_args().AndReturn(("options", ['test']))
    b = bob.Bob(parser=mock_parser)
    b.test = mox.CreateMockAnything()
    b.test()

    mox.ReplayAll()
    b.run()
    mox.VerifyAll()

def test_go_through_run():
    mox = Mox()

    mock_parser = mox.CreateMockAnything()
    mock_parser.parse_args().AndReturn(('should_be_options', ['go']))

    options_mock = mox.CreateMockAnything()

    file_system = mox.CreateMockAnything()

    b = bob.Bob(parser=mock_parser, fs=file_system)
    b.go = mox.CreateMockAnything()
    b.go()
    mox.ReplayAll()

    try:
        got = b.run()
        mox.VerifyAll()
    finally:
        mox.UnsetStubs()

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

    mox.StubOutWithMock(bob, 'syck')
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
    bob.syck.load('should-be-raw-yaml-text'). \
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
