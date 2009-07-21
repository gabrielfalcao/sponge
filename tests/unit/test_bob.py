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

import yaml
import cherrypy
import optparse

from os.path import abspath, join, dirname
from mox import Mox
from nose.tools import assert_equals
from sponge import bob

def test_can_create_bob():
    b = bob.Bob()
    assert b
    assert isinstance(b, bob.Bob)

def test_run():
    mox = Mox()

    mock_parser = mox.CreateMockAnything()
    mock_parser.parse_args().AndReturn(("options", "args"))

    mox.ReplayAll()

    b = bob.Bob(parser=mock_parser)
    b.run()

    mox.VerifyAll()

def test_create_project_raises_if_folder_already_exists():
    mox = Mox()

    mock_parser = mox.CreateMockAnything()

    options_mock = mox.CreateMockAnything()
    options_mock.project_dir = "something"

    file_system = mox.CreateMockAnything()
    file_system.join("something", "some project").AndReturn("something/some project")
    file_system.abspath("something/some project").AndReturn("/something/some project")
    file_system.exists("/something/some project").AndReturn(True)

    mox.ReplayAll()

    b = bob.Bob(parser=mock_parser, fs=file_system)
    try:
        b.create_project(options_mock,"some project")
    except bob.Bob.ProjectFolderExists, err:
        assert str(err) == "There is a folder at '/something/some project' already, thus making it impossible to create a project there."
        mox.VerifyAll()
        return

    assert False, "Should not have reached this far."

def test_create_project_creates_folder_if_one_does_not_exist():
    mox = Mox()

    mock_parser = mox.CreateMockAnything()

    options_mock = mox.CreateMockAnything()
    options_mock.project_dir = "something"

    file_system = mox.CreateMockAnything()
    file_system.join("something", "some project").AndReturn("something/some project")
    file_system.abspath("something/some project").AndReturn("/something/some project")
    file_system.exists("/something/some project").AndReturn(False)
    file_system.mkdir("/something/some project")

    b = bob.Bob(parser=mock_parser, fs=file_system)
    mox.StubOutWithMock(b, 'create_project_structure')
    b.create_project_structure(options_mock, "some project", "/something/some project")

    mox.ReplayAll()

    try:
        b.create_project(options_mock,"some project")
        mox.VerifyAll()
    finally:
        mox.UnsetStubs()

def test_create_project_calls_create_structure():
    mox = Mox()

    mock_parser = mox.CreateMockAnything()
    options_mock = mox.CreateMockAnything()
    options_mock.project_dir = "something"

    file_system = mox.CreateMockAnything()
    file_system.join("something", "some project").AndReturn("something/some project")
    file_system.abspath("something/some project").AndReturn("/something/some project")
    file_system.exists("/something/some project").AndReturn(False)
    file_system.mkdir("/something/some project")

    b = bob.Bob(parser=mock_parser, fs=file_system)
    mox.StubOutWithMock(b, 'create_project_structure')
    b.create_project_structure(options_mock, "some project", "/something/some project")
    mox.ReplayAll()

    try:
        b.create_project(options_mock,"some project")
        mox.VerifyAll()
    finally:
        mox.UnsetStubs()

def test_create_structure():
    mox = Mox()
    mock_parser = mox.CreateMockAnything()

    options_mock = mox.CreateMockAnything()
    options_mock.project_dir = "something"

    file_system = mox.CreateMockAnything()

    b = bob.Bob(parser=mock_parser, fs=file_system)

    file_path = bob.Bob.get_file_path
    bob.Bob.get_file_path = lambda self: "fake file"

    path = "/some/path/to/fake file"

    file_system.dirname('fake file').AndReturn("/some/path/to/fake file")
    file_system.join(path, "templates", "create_project").AndReturn("templates/create_project")
    file_system.abspath("templates/create_project").AndReturn("/templates/create_project")

    file_system.locate(path="/templates/create_project", match="*.*", recursive=True).AndReturn(["/templates/create_project/some_file.txt"])
    file_system.rebase(destiny_folder='/something/some project', origin_folder='/templates/create_project', path='/templates/create_project/some_file.txt').AndReturn("/something/some project/some_file.txt")

    file_system.read_all(encoding='utf-8', path='/templates/create_project/some_file.txt').AndReturn("some template")
    file_system.write_all(contents='some template', create_dir=True, encoding='utf-8', path='/something/some project/some_file.txt')

    mox.ReplayAll()

    b.create_project_structure(options_mock, "some project", "/something/some project")
    mox.VerifyAll()

def test_create_project_through_run():
    mox = Mox()

    mock_parser = mox.CreateMockAnything()
    mock_parser.parse_args().AndReturn(('should_be_options', ['create', 'should_be_project_name']))

    options_mock = mox.CreateMockAnything()
    options_mock.project_dir = "something"

    file_system = mox.CreateMockAnything()

    b = bob.Bob(parser=mock_parser, fs=file_system)
    b.create_project = mox.CreateMockAnything()
    b.create_project('should_be_options', 'should_be_project_name')
    mox.ReplayAll()

    try:
        got = b.run()
        assert got is 0, 'Expected 0, got %s' % repr(got)
        mox.VerifyAll()
    finally:
        mox.UnsetStubs()

def test_bob_go():
    mox = Mox()

    class_loader = bob.ClassLoader
    mock_parser = mox.CreateMockAnything()
    bob.ClassLoader = mox.CreateMockAnything()

    mox.StubOutWithMock(bob, 'codecs')

    mox.StubOutWithMock(bob.cherrypy, 'tree')
    mox.StubOutWithMock(bob.cherrypy, 'server')
    mox.StubOutWithMock(bob.cherrypy, 'engine')

    mox.StubOutWithMock(bob, 'yaml')

    config_dict = {
        'run-as': 'wsgi',
        'host': '0.0.0.0',
        'port': 80,
        'autoreload': False,
        'application': {
            'path': '/path/to/project',
            'template-dir': '/path/to/project/templates',
            'image-dir': '/path/to/project/images',
            'classes': {
                'SomeController': '/'
            }
        }
    }

    file_object_mock = mox.CreateMockAnything()
    raw_yaml = yaml.dump(config_dict)
    file_object_mock.read().AndReturn(raw_yaml)
    bob.codecs.open('/full/path/to/settings.yml', 'r', 'utf-8').AndReturn(file_object_mock)
    bob.yaml.load(raw_yaml).AndReturn(config_dict)

    options_mock = mox.CreateMockAnything()
    file_system = mox.CreateMockAnything()
    file_system.current_dir('settings.yml').AndReturn('/full/path/to/settings.yml')

    class_loader_mock = mox.CreateMockAnything()
    controller_mock = mox.CreateMockAnything()
    bob.ClassLoader('/path/to/project').AndReturn(class_loader_mock)
    class_loader_mock.load('SomeController').AndReturn(controller_mock)
    cherrypy.tree.mount(controller_mock().AndReturn(controller_mock), '/')
    cherrypy.server.quickstart()
    cherrypy.engine.start()
    cherrypy.engine.block()

    b = bob.Bob(parser=mock_parser, fs=file_system)
    mox.ReplayAll()

    try:
        got = b.go()
        assert cherrypy.config.has_key('sponge'), \
               'After invoking Bob.go, cherrypy.config should ' \
               'have the key "sponge"'
        assert_equals(cherrypy.config['sponge'], config_dict)

        mox.VerifyAll()

    finally:
        mox.UnsetStubs()
        bob.ClassLoader = class_loader
