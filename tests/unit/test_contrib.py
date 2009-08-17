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
import cherrypy

from mox import Mox
from nose.tools import assert_equal
from utils import assert_raises
from sponge.contrib import controllers

class TestImageHandler:
    def __init__(self):
        self.handler = controllers.ImageHandler()

    def test_is_exposed(self):
        message = 'The ImageHandler should be exposed, ' \
                  'so that CherryPy can see it'
        assert self.handler.exposed is True, message

    def test_return_not_found_with_no_args(self):
        got = self.handler()
        msg1 = 'the response should be "not found", got %s' % repr(got)
        msg2 = 'The response status code should be 404, got %r' % \
               cherrypy.response.status
        assert got == 'not found', msg1
        assert cherrypy.response.status == 404, msg2

    def test_calls_jpeg_when_args_length_less_than_3(self):
        mox = Mox()

        mox.StubOutWithMock(controllers, 'jpeg')
        ret = 'should_be_a_pil_img'
        controllers.jpeg(path='arg1/arg2').AndReturn(ret)

        mox.ReplayAll()
        got = self.handler('arg1', 'arg2')
        mox.VerifyAll()

        msg = 'Expected "%s", got %r' % (ret, got)
        assert got == ret, msg

    def test_calls_jpeg_when_args_length_equals_3(self):
        mox = Mox()

        mox.StubOutWithMock(controllers, 'jpeg')
        ret = 'should_be_a_pil_img'
        controllers.jpeg(path='arg1/arg2/arg3').AndReturn(ret)

        mox.ReplayAll()
        got = self.handler('arg1', 'arg2', 'arg3')
        mox.VerifyAll()

        msg = 'Expected "%s", got %r' % (ret, got)
        assert got == ret, msg

    def test_calls_jpeg_when_args_length_bigger_than_3_no_crop(self):
        mox = Mox()

        mox.StubOutWithMock(controllers, 'jpeg')
        ret = 'should_be_a_pil_img'
        controllers.jpeg(path='arg1/arg2/arg3/arg4').AndReturn(ret)

        mox.ReplayAll()
        got = self.handler('arg1', 'arg2', 'arg3', 'arg4')
        mox.VerifyAll()

        msg = 'Expected "%s", got %r' % (ret, got)
        assert got == ret, msg

    def test_calls_jpeg_when_args_length_bigger_than_3_crop_no_proportion(self):
        mox = Mox()

        mox.StubOutWithMock(controllers, 'jpeg')
        ret = 'should_be_a_pil_img'
        controllers.jpeg(path='crop/arg2/arg3/arg4').AndReturn(ret)

        mox.ReplayAll()
        got = self.handler('crop', 'arg2', 'arg3', 'arg4')
        mox.VerifyAll()

        msg = 'Expected "%s", got %r' % (ret, got)
        assert got == ret, msg

    def test_calls_jpeg_when_args_length_equals_3_and_crop(self):
        mox = Mox()

        mox.StubOutWithMock(controllers, 'jpeg')
        mox.StubOutWithMock(controllers, 'picture')

        ret = 'should_be_a_pil_img'

        controllers.jpeg(path='crop/200x100/image.jpg')
        controllers.picture(path='image.jpg', width=200, height=100). \
                                             AndReturn(ret)

        mox.ReplayAll()
        got = self.handler('crop', '200x100', 'image.jpg')
        mox.VerifyAll()

        msg = 'Expected "%s", got %r' % (ret, got)
        assert got == ret, msg

    def test_creation_takes_optional_cache_path_string(self):
        assert_raises(TypeError, controllers.ImageHandler, 5,
                      exc_pattern=r'The path given to ImageHandler ' \
                      'to cache must be a string, got 5')

    def test_caching_fails_if_cache_path_does_not_exist(self):
        mox = Mox()

        class ImageHandlerStub(controllers.ImageHandler):
            fs = mox.CreateMockAnything()

        ImageHandlerStub.fs.exists('/full/path/to/cache').AndReturn(False)

        mox.ReplayAll()
        assert_raises(controllers.InvalidCachePath,
                      ImageHandlerStub,
                      '/full/path/to/cache',
                      exc_pattern=r'The given path \(/full/path/to/cache\) ' \
                      'does not exist, so that ImageHandler can not save ' \
                      'cache files there.')
        mox.VerifyAll()

    def test_caching_return_if_already_exists(self):
        mox = Mox()

        old_jpeg = controllers.jpeg
        old_picture = controllers.picture
        old_static = controllers.static

        mox.StubOutWithMock(controllers, 'static')
        controllers.jpeg = mox.CreateMockAnything()
        controllers.picture = mox.CreateMockAnything()

        cache_at = '/full/path/to/cache'
        class ImageHandlerStub(controllers.ImageHandler):
            fs = mox.CreateMockAnything()

        ImageHandlerStub.fs.exists(cache_at).AndReturn(True)

        controllers.jpeg(path='imgs/image.jpg')
        ImageHandlerStub.fs.join(cache_at, 'imgs/image.jpg'). \
                         AndReturn('/should/be/cache/full/path.jpg')

        ImageHandlerStub.fs.exists('/should/be/cache/full/path.jpg'). \
                         AndReturn(True)
        controllers.static.serve_file('/should/be/cache/full/path.jpg',
                              'image/jpeg'). \
                   AndReturn('should-be-image-data')

        mox.ReplayAll()
        try:
            img = ImageHandlerStub(cache_at)
            assert img.should_cache
            assert_equal(img.cache_path, cache_at)
            got = img('imgs', 'image.jpg')
            assert_equal(got, 'should-be-image-data')
            mox.VerifyAll()
        finally:
            controllers.jpeg = old_jpeg
            controllers.picture = old_picture
            mox.UnsetStubs()

    def test_caching_opens_if_does_not_exist(self):
        mox = Mox()

        old_jpeg = controllers.jpeg
        old_picture = controllers.picture
        controllers.jpeg = mox.CreateMockAnything()
        controllers.picture = mox.CreateMockAnything()

        cache_at = '/full/path/to/cache'
        class ImageHandlerStub(controllers.ImageHandler):
            fs = mox.CreateMockAnything()

        ImageHandlerStub.fs.exists(cache_at).AndReturn(True)

        controllers.jpeg(path='imgs/image.jpg').AndReturn('fake-img')
        ImageHandlerStub.fs.join(cache_at, 'imgs/image.jpg'). \
                         AndReturn('/should/be/cache/full/path.jpg')

        ImageHandlerStub.fs.exists('/should/be/cache/full/path.jpg'). \
                         AndReturn(False)

        ImageHandlerStub.fs.dirname('/should/be/cache/full/path.jpg'). \
                         AndReturn('dir-name')

        ImageHandlerStub.fs.mkdir('dir-name')

        file_mock = mox.CreateMockAnything()
        ImageHandlerStub.fs.open_raw('/should/be/cache/full/path.jpg', 'w'). \
                         AndReturn(file_mock)

        file_mock.write('fake-img')
        file_mock.close()

        mox.ReplayAll()
        try:
            img = ImageHandlerStub(cache_at)
            assert img.should_cache
            assert_equal(img.cache_path, cache_at)
            got = img('imgs', 'image.jpg')
            assert_equal(got, 'fake-img')
            mox.VerifyAll()
        finally:
            controllers.jpeg = old_jpeg
            controllers.picture = old_picture

