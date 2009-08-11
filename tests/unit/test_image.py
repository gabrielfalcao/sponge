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
import Image
import cherrypy

from mox import Mox
from utils import assert_raises
from os.path import join

from sponge.helpers import image

def test_image_has_function_jpeg():
    assert hasattr(image, 'jpeg'), 'sponge.image should have the function jpeg'
    assert callable(image.jpeg), 'sponge.image.jpeg should be callable'

def test_jpeg_takes_path_as_param():
    assert_raises(TypeError, image.jpeg, exc_pattern=r'jpeg.. takes at least 1 argument .0 given.')

def test_jpeg_param_should_be_string():
    assert_raises(TypeError, image.jpeg, None, exc_pattern=r'jpeg.. takes a string as parameter, got None.')

def test_jpeg_success():
    mox = Mox()

    path = '/path/to/mocked/img.jpg'

    mox.StubOutWithMock(image, 'Image')
    mox.StubOutWithMock(image, 'StringIO')

    stringio_mock = mox.CreateMockAnything()
    return_mock = mox.CreateMockAnything()
    img_mock = mox.CreateMockAnything()

    stringio_mock.getvalue().AndReturn(return_mock)

    image.StringIO.StringIO().AndReturn(stringio_mock)
    image.Image.open(path).AndReturn(img_mock)

    img_mock.save(stringio_mock, "JPEG", quality=100)

    cherrypy.config['image.dir'] = path

    mox.ReplayAll()

    return_got = image.jpeg(path)
    assert return_got == return_mock, 'The return of image.jpeg() should be %r, got %r' % (return_mock, return_got)
    mime = cherrypy.response.headers['Content-type']
    assert mime == 'image/jpeg', 'The response header "Content-type" should be image/jpeg, but got %r' % mime

    mox.VerifyAll()

    del cherrypy.config['image.dir']

def test_jpeg_return_string_when_file_not_found():
    filename = 'foo-file.jpg'
    path = join('bazbar', filename)
    mox = Mox()

    mox.StubOutWithMock(image, 'Image')

    image.Image.open(path).AndRaise(IOError('File not found: foo-file.jpg'))

    mox.ReplayAll()
    ret = image.jpeg(filename, base_path='bazbar')

    assert isinstance(ret, unicode), 'The return value should be unicode, but is %r' % type(ret)
    assert ret == 'File not found: foo-file.jpg', 'Wrong error description: %r' % ret

    mox.VerifyAll()

def test_crop_to_fit_bigger():
    img = Image.new('RGBA', (653, 342))
    ret = image.crop_to_fit(img, (320, 240))
    assert ret.size == (320, 240), 'Got expected size 320x240, got %rx%r.' % ret.size

def test_crop_to_fit_lower():
    img = Image.new('RGBA', (500, 750))
    ret = image.crop_to_fit(img, (320, 240))
    assert ret.size == (320, 240), 'Got expected size 320x240, got %rx%r.' % ret.size

def test_picture_takes_3_parameters():
    assert_raises(TypeError, image.picture, exc_pattern=r'picture.. takes at least 3 arguments .0 given.')

def test_picture_first_param_should_be_string():
    assert_raises(TypeError, image.picture, None, None, None, exc_pattern=r'picture.. takes a string as path parameter, got None.')

def test_picture_second_param_should_be_int():
    assert_raises(TypeError, image.picture, '', None, None, exc_pattern=r'picture.. takes a integer as width parameter, got None.')

def test_picture_third_param_should_be_int():
    assert_raises(TypeError, image.picture, '', 1, None, exc_pattern=r'picture.. takes a integer as height parameter, got None.')

def test_picture_with_crop_true_will_crop_to_fit():
    base_path = '/basepath/for/test_picture_success'
    path = 'my_picture.jpg'

    mox = Mox()

    mox.StubOutWithMock(image, 'Image')
    mox.StubOutWithMock(image, 'StringIO')
    mox.StubOutWithMock(image, 'crop_to_fit')

    img_mock = mox.CreateMockAnything()
    img_mock.size = 300, 300

    stringio_mock = mox.CreateMockAnything()
    return_mock = mox.CreateMockAnything()

    stringio_mock.getvalue().AndReturn(return_mock)

    image.StringIO.StringIO().AndReturn(stringio_mock)

    cherrypy.config['image.dir'] = base_path

    image.Image.open(join(base_path, path)).AndReturn(img_mock)
    img_mock.save(stringio_mock, 'JPEG', quality=100)
    image.crop_to_fit(img_mock, (100, 100)).AndReturn(img_mock)

    mox.ReplayAll()

    ret = image.picture(path, 100, 100, crop=True, center=False)
    assert ret == return_mock, "Expected %r. Got %r." % (return_mock, ret)

    mox.VerifyAll()
    del cherrypy.config['image.dir']

def test_picture_with_center_true_will_create_new_image_and_paste():
    base_path = '/base/path'
    path = 'image.jpg'

    mox = Mox()

    mox.StubOutWithMock(image, 'Image')
    mox.StubOutWithMock(image, 'StringIO')

    img_mock = mox.CreateMockAnything()
    img_mock.size = 300, 300

    stringio_mock = mox.CreateMockAnything()
    return_mock = mox.CreateMockAnything()

    stringio_mock.getvalue().AndReturn(return_mock)
    image.StringIO.StringIO().AndReturn(stringio_mock)

    cherrypy.config['image.dir'] = base_path

    new_img_mock = mox.CreateMockAnything()

    new_img_mock.paste(img_mock, (-100, -100))
    new_img_mock.save(stringio_mock, 'JPEG', quality=100)

    image.Image.open(join(base_path, path)).AndReturn(img_mock)
    image.Image.new('RGBA', (100, 100), 0xffffff).AndReturn(new_img_mock)

    mox.ReplayAll()
    ret = image.picture(path, 100, 100, crop=False, center=True)

    assert ret == return_mock, "Expected %r. Got %r." % (return_mock, ret)
    mox.VerifyAll()

    del cherrypy.config['image.dir']
