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
from sponge import controller

class TestImageHandler:
    def __init__(self):
        self.handler = controller.ImageHandler()

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

        mox.StubOutWithMock(controller, 'jpeg')
        ret = 'should_be_a_pil_img'
        controller.jpeg(path='arg1/arg2').AndReturn(ret)

        mox.ReplayAll()
        got = self.handler('arg1', 'arg2')
        mox.VerifyAll()

        msg = 'Expected "%s", got %r' % (ret, got)
        assert got == ret, msg

    def test_calls_jpeg_when_args_length_equals_3(self):
        mox = Mox()

        mox.StubOutWithMock(controller, 'jpeg')
        ret = 'should_be_a_pil_img'
        controller.jpeg(path='arg1/arg2/arg3').AndReturn(ret)

        mox.ReplayAll()
        got = self.handler('arg1', 'arg2', 'arg3')
        mox.VerifyAll()

        msg = 'Expected "%s", got %r' % (ret, got)
        assert got == ret, msg

    def test_calls_jpeg_when_args_length_bigger_than_3_no_crop(self):
        mox = Mox()

        mox.StubOutWithMock(controller, 'jpeg')
        ret = 'should_be_a_pil_img'
        controller.jpeg(path='arg1/arg2/arg3/arg4').AndReturn(ret)

        mox.ReplayAll()
        got = self.handler('arg1', 'arg2', 'arg3', 'arg4')
        mox.VerifyAll()

        msg = 'Expected "%s", got %r' % (ret, got)
        assert got == ret, msg

    def test_calls_jpeg_when_args_length_bigger_than_3_crop_no_proportion(self):
        mox = Mox()

        mox.StubOutWithMock(controller, 'jpeg')
        ret = 'should_be_a_pil_img'
        controller.jpeg(path='crop/arg2/arg3/arg4').AndReturn(ret)

        mox.ReplayAll()
        got = self.handler('crop', 'arg2', 'arg3', 'arg4')
        mox.VerifyAll()

        msg = 'Expected "%s", got %r' % (ret, got)
        assert got == ret, msg

    def test_calls_jpeg_when_args_length_equals_3_and_crop(self):
        mox = Mox()

        mox.StubOutWithMock(controller, 'jpeg')
        mox.StubOutWithMock(controller, 'picture')

        ret = 'should_be_a_pil_img'

        controller.jpeg(path='crop/200x100/image.jpg')
        controller.picture(path='image.jpg', width=200, height=100). \
                                             AndReturn(ret)

        mox.ReplayAll()
        got = self.handler('crop', '200x100', 'image.jpg')
        mox.VerifyAll()

        msg = 'Expected "%s", got %r' % (ret, got)
        assert got == ret, msg
