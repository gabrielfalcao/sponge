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

import optparse

import os
from os.path import abspath, join, dirname

from mox import Mox

from sponge.bob import *

def test_can_create_bob():
    b = Bob()
    assert b
    assert isinstance(b, Bob)

def test_run():
    mox = Mox()

    mock_parser = mox.CreateMockAnything()
    mock_parser.parse_args().AndReturn(("options", "args"))

    mox.ReplayAll()

    b = Bob(parser=mock_parser)
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

    b = Bob(parser=mock_parser, fs=file_system)
    try:
        b.create_project(options_mock,"some project")
    except Bob.ProjectFolderExists, err:
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

    b = Bob(parser=mock_parser, fs=file_system)
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

    b = Bob(parser=mock_parser, fs=file_system)
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

    b = Bob(parser=mock_parser, fs=file_system)

    file_path = Bob.get_file_path
    Bob.get_file_path = lambda self: "fake file"

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

    b = Bob(parser=mock_parser, fs=file_system)
    b.create_project = mox.CreateMockAnything()
    b.create_project('should_be_options', 'should_be_project_name')
    mox.ReplayAll()

    try:
        got = b.run()
        assert got is 0, 'Expected 0, got %s' % repr(got)
        mox.VerifyAll()
    finally:
        mox.UnsetStubs()
