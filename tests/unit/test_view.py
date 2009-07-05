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
import Image
import cherrypy
from os.path import join
from sponge import view
from utils import assert_raises
from pmock import *

def test_view_has_make_url_function():
    assert hasattr(view, 'make_url'), 'sponge.view should have the function make_url'
    assert callable(view.make_url), 'sponge.view.make_url should be callable'

def test_make_url_takes_string_as_param():
    expected = r'sponge.view.make_url ' \
               'takes a string as param, got None.'
    assert_raises(TypeError, view.make_url, None, exc_pattern=expected)

def test_make_url_without_trailling_slash():
    base_url = 'http://my.unit.test/for/ma-cherie'
    cherrypy.request.base = base_url

    expected_url = 'http://my.unit.test/for/ma-cherie/index'
    got_url = view.make_url('index')
    assert got_url == expected_url, 'Expected %s, got %s' % (expected_url, got_url)

def test_make_url_with_trailling_slash_on_base_url():
    base_url = 'http://my.unit.test/for/ma-cherie/'
    cherrypy.request.base = base_url

    expected_url = 'http://my.unit.test/for/ma-cherie/index'
    got_url = view.make_url('index')
    assert got_url == expected_url, 'Expected %s, got %s' % (expected_url, got_url)

def test_make_url_with_trailling_slash_on_url_part():
    base_url = 'http://my.unit.test/for/ma-cherie'
    cherrypy.request.base = base_url

    expected_url = 'http://my.unit.test/for/ma-cherie/index'
    got_url = view.make_url('/index')
    assert got_url == expected_url, 'Expected %s, got %s' % (expected_url, got_url)

def test_make_url_with_trailling_slash_on_both():
    base_url = 'http://my.unit.test/for/ma-cherie/'
    cherrypy.request.base = base_url

    expected_url = 'http://my.unit.test/for/ma-cherie/index'
    got_url = view.make_url('/index')
    assert got_url == expected_url, 'Expected %s, got %s' % (expected_url, got_url)

def test_view_has_function_render_html():
    assert hasattr(view, 'render_html'), 'sponge.view should have the function render_html'
    assert callable(view.render_html), 'sponge.view.render_html should be callable'

def test_view_has_function_jpeg():
    assert hasattr(view, 'jpeg'), 'sponge.view should have the function jpeg'
    assert callable(view.jpeg), 'sponge.view.jpeg should be callable'

def test_jpeg_takes_path_as_param():
    assert_raises(TypeError, view.jpeg, exc_pattern=r'jpeg.. takes at least 1 argument .0 given.')

def test_jpeg_param_should_be_string():
    assert_raises(TypeError, view.jpeg, None, exc_pattern=r'jpeg.. takes a string as parameter, got None.')

def test_jpeg_success():
    path = '/path/to/mocked/img.jpg'
    img_mock = Mock()
    pil_mock = Mock()
    stringio_module_mock = Mock()
    stringio_mock = Mock()
    return_mock = Mock()

    stringio_mock.expects(once()).getvalue().will(return_value(return_mock))

    stringio_module_mock.expects(once()).StringIO().will(return_value(stringio_mock))

    pil_mock.expects(once()).open(eq(path)).will(return_value(img_mock))

    img_mock.expects(once()).save(eq(stringio_mock), eq("JPEG"), quality=eq(100))

    Image = view.Image
    StringIO = view.StringIO
    view.StringIO = stringio_module_mock
    view.Image = pil_mock
    return_got = view.jpeg(path)

    pil_mock.verify()
    stringio_module_mock.verify()
    img_mock.verify()
    stringio_mock.verify()
    assert return_got == return_mock, 'The return of view.jpeg() should be %r, got %r' % (return_mock, return_got)
    mime = cherrypy.response.headers['Content-type']
    assert mime == 'image/jpeg', 'The response header "Content-type" should be image/jpeg, but got %r' % mime

    view.Image = Image
    view.StringIO = StringIO

def test_jpeg_return_string_when_file_not_found():
    filename = 'foo-file.jpg'
    path = join('bazbar', filename)
    pil_mock = Mock()
    Image = view.Image
    view.Image = pil_mock

    pil_mock.expects(once()).open(eq(path)).will(raise_exception(IOError('File not found: foo-file.jpg')))
    ret = view.jpeg(filename, base_path='bazbar')
    pil_mock.verify()

    assert isinstance(ret, unicode), 'The return value should be unicode, but is %r' % type(ret)
    assert ret == 'File not found: foo-file.jpg', 'Wrong error description: %r' % ret
    view.Image = Image

def test_crop_to_fit_bigger():
    img = Image.new('RGBA', (653, 342))
    ret = view.crop_to_fit(img, (320, 240))
    assert ret.size == (320, 240), 'Got expected size 320x240, got %rx%r.' % ret.size

def test_crop_to_fit_lower():
    img = Image.new('RGBA', (300, 200))
    ret = view.crop_to_fit(img, (600, 500))
    assert ret.size == (600, 500), 'Got expected size 320x240, got %rx%r.' % ret.size

def test_picture_takes_3_parameters():
    assert_raises(TypeError, view.picture, exc_pattern=r'picture.. takes at least 3 arguments .0 given.')

def test_picture_first_param_should_be_string():
    assert_raises(TypeError, view.picture, None, None, None, exc_pattern=r'picture.. takes a string as path parameter, got None.')

def test_picture_second_param_should_be_int():
    assert_raises(TypeError, view.picture, '', None, None, exc_pattern=r'picture.. takes a integer as width parameter, got None.')

def test_picture_third_param_should_be_int():
    assert_raises(TypeError, view.picture, '', 1, None, exc_pattern=r'picture.. takes a integer as height parameter, got None.')

def test_picture_with_crop_true_will_crop_to_fit():
    base_path = '/basepath/for/test_picture_success'
    path = 'my_picture.jpg'
    img_mock = Mock()
    img_mock.size = 300, 300
    pil_mock = Mock()

    stringio_module_mock = Mock()
    stringio_mock = Mock()
    return_mock = Mock()

    stringio_mock.expects(once()).getvalue().will(return_value(return_mock))

    stringio_module_mock.expects(once()).StringIO().will(return_value(stringio_mock))

    Image = view.Image
    crop_to_fit = view.crop_to_fit
    old_basepath = view.base_path
    StringIO = view.StringIO

    functions_mock = Mock()
    functions_mock.expects(once()).crop_to_fit(eq(img_mock), eq((100, 100))).will(return_value(img_mock))
    view.Image = pil_mock
    view.base_path = base_path
    view.StringIO = stringio_module_mock
    view.crop_to_fit = functions_mock.crop_to_fit
    pil_mock.expects(once()).open(eq(join(base_path, path))).will(return_value(img_mock))
    img_mock.expects(once()).save(eq(stringio_mock), eq('JPEG'), quality=eq(100))
    ret = view.picture(path, 100, 100, crop=True, center=False)

    pil_mock.verify()
    img_mock.verify()
    stringio_mock.verify()
    stringio_module_mock.verify()
    functions_mock.verify()
    view.Image = Image
    view.crop_to_fit = crop_to_fit
    view.base_path = old_basepath
    view.StringIO = StringIO

    assert ret == return_mock, "Expected %r. Got %r." % (return_mock, ret)

def test_picture_with_center_true_will_create_new_image_and_paste():
    base_path = '/base/path'
    path = 'image.jpg'
    img_mock = Mock()

    img_mock.size = 300, 300
    pil_mock = Mock()

    stringio_module_mock = Mock()
    stringio_mock = Mock()
    return_mock = Mock()

    stringio_mock.expects(once()).getvalue().will(return_value(return_mock))
    stringio_module_mock.expects(once()).StringIO().will(return_value(stringio_mock))

    Image = view.Image
    old_basepath = view.base_path
    StringIO = view.StringIO

    view.Image = pil_mock
    view.base_path = base_path
    view.StringIO = stringio_module_mock

    new_img_mock = Mock()

    new_img_mock.expects(once()).save(eq(stringio_mock), eq('JPEG'), quality=eq(100))
    new_img_mock.expects(once()).paste(eq(img_mock), eq((-100, -100)))

    pil_mock.expects(once()).new(eq('RGBA'), eq((100, 100)), eq(0xffffff)).will(return_value(new_img_mock))
    pil_mock.expects(once()).open(eq(join(base_path, path))).will(return_value(img_mock))

    ret = view.picture(path, 100, 100, crop=False, center=True)

    pil_mock.verify()
    img_mock.verify()
    stringio_mock.verify()
    stringio_module_mock.verify()

    view.Image = Image
    view.base_path = old_basepath
    view.StringIO = StringIO
    assert ret == return_mock, "Expected %r. Got %r." % (return_mock, ret)
