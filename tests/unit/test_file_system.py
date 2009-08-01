# -*- coding: utf-8 -*-
import os
from mox import Mox
from nose.tools import assert_equals
from utils import assert_raises
from sponge.core import io

def test_has_a_stack_list():
    assert hasattr(io.FileSystem, 'stack'), \
           'FileSystem should have a stack'
    assert isinstance(io.FileSystem.stack, list), \
           'FileSystem.stack should be a list'

def test_instance_stack_is_not_the_same_as_class_level():
    class MyFs(io.FileSystem):
        pass

    MyFs.stack.append('foo')
    MyFs.stack.append('bar')
    assert_equals(MyFs().stack, [])

def test_pushd_appends_current_dir_to_stack_if_empty():
    mox = Mox()
    old_os = io.os
    io.os = mox.CreateMockAnything()

    class MyFs(io.FileSystem):
        stack = []

        @classmethod
        def current_dir(cls):
            return 'should be current dir'

    io.os.chdir('somewhere')

    mox.ReplayAll()
    try:
        assert len(MyFs.stack) is 0
        MyFs.pushd('somewhere')
        assert len(MyFs.stack) is 2
        assert_equals(MyFs.stack, ['should be current dir',
                                   'somewhere'])
        mox.VerifyAll()
    finally:
        io.os = old_os

def test_pushd():
    mox = Mox()
    old_os = io.os
    io.os = mox.CreateMockAnything()

    class MyFs(io.FileSystem):
        stack = ['first']

    io.os.chdir('second')

    mox.ReplayAll()
    try:
        assert len(MyFs.stack) is 1
        MyFs.pushd('second')
        assert len(MyFs.stack) is 2
        assert_equals(MyFs.stack, ['first',
                                   'second'])
        mox.VerifyAll()
    finally:
        io.os = old_os

def test_pop_with_more_than_1_item():
    mox = Mox()
    old_os = io.os
    io.os = mox.CreateMockAnything()

    class MyFs(io.FileSystem):
        stack = ['one', 'two']

    io.os.chdir('one')

    mox.ReplayAll()
    try:
        assert len(MyFs.stack) is 2
        MyFs.popd()
        assert len(MyFs.stack) is 1
        assert_equals(MyFs.stack, ['one'])
        mox.VerifyAll()
    finally:
        io.os = old_os

def test_pop_with_1_item():
    mox = Mox()
    old_os = io.os
    io.os = mox.CreateMockAnything()

    class MyFs(io.FileSystem):
        stack = ['one']

    mox.ReplayAll()
    try:
        assert len(MyFs.stack) is 1
        MyFs.popd()
        assert len(MyFs.stack) is 0
        assert_equals(MyFs.stack, [])
        mox.VerifyAll()
    finally:
        io.os = old_os

def test_pop_with_no_item():
    mox = Mox()
    old_os = io.os
    io.os = mox.CreateMockAnything()

    class MyFs(io.FileSystem):
        stack = []

    mox.ReplayAll()
    try:
        assert len(MyFs.stack) is 0
        MyFs.popd()
        assert len(MyFs.stack) is 0
        assert_equals(MyFs.stack, [])
        mox.VerifyAll()
    finally:
        io.os = old_os

def test_filename_with_extension():
    got = io.FileSystem.filename('/path/to/filename.jpg')
    assert_equals(got, 'filename.jpg')

def test_filename_without_extension():
    got = io.FileSystem.filename('/path/to/filename.jpg', False)
    assert_equals(got, 'filename')

def test_dirname():
    got = io.FileSystem.dirname('/path/to/filename.jpg')
    assert_equals(got, '/path/to')

def test_exists():
    mox = Mox()
    old_exists = io.exists
    io.exists = mox.CreateMockAnything()

    io.exists('some path').AndReturn('should be bool')

    mox.ReplayAll()
    try:
        got = io.FileSystem.exists('some path')
        assert_equals(got, 'should be bool')
        mox.VerifyAll()
    finally:
        io.exists = old_exists
