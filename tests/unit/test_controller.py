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

    def test_creation_takes_optional_cache_path_string(self):
        assert_raises(TypeError, controller.ImageHandler, 5,
                      exc_pattern=r'The path given to ImageHandler ' \
                      'to cache must be a string, got 5')

    def test_caching_fails_if_cache_path_does_not_exist(self):
        mox = Mox()

        class ImageHandlerStub(controller.ImageHandler):
            fs = mox.CreateMockAnything()

        ImageHandlerStub.fs.exists('/full/path/to/cache').AndReturn(False)

        mox.ReplayAll()
        assert_raises(controller.InvalidCachePath,
                      ImageHandlerStub,
                      '/full/path/to/cache',
                      exc_pattern=r'The given path \(/full/path/to/cache\) ' \
                      'does not exist, so that ImageHandler can not save ' \
                      'cache files there.')
        mox.VerifyAll()

    def test_caching_return_if_already_exists(self):
        mox = Mox()

        old_jpeg = controller.jpeg
        old_picture = controller.picture
        old_serve_file = controller.serve_file

        controller.jpeg = mox.CreateMockAnything()
        controller.picture = mox.CreateMockAnything()
        controller.serve_file = mox.CreateMockAnything()

        cache_at = '/full/path/to/cache'
        class ImageHandlerStub(controller.ImageHandler):
            fs = mox.CreateMockAnything()

        ImageHandlerStub.fs.exists(cache_at).AndReturn(True)

        controller.jpeg(path='imgs/image.jpg')
        ImageHandlerStub.fs.join(cache_at, 'imgs/image.jpg'). \
                         AndReturn('/should/be/cache/full/path.jpg')

        ImageHandlerStub.fs.exists('/should/be/cache/full/path.jpg'). \
                         AndReturn(True)
        controller.serve_file('/should/be/cache/full/path.jpg',
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
            controller.jpeg = old_jpeg
            controller.picture = old_picture
            controller.serve_file = old_serve_file

    def test_caching_return_if_already_exists(self):
        mox = Mox()

        old_jpeg = controller.jpeg
        old_picture = controller.picture
        old_serve_file = controller.serve_file

        controller.jpeg = mox.CreateMockAnything()
        controller.picture = mox.CreateMockAnything()
        controller.serve_file = mox.CreateMockAnything()

        cache_at = '/full/path/to/cache'
        class ImageHandlerStub(controller.ImageHandler):
            fs = mox.CreateMockAnything()

        ImageHandlerStub.fs.exists(cache_at).AndReturn(True)

        controller.jpeg(path='imgs/image.jpg').AndReturn('fake-img')
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
            controller.jpeg = old_jpeg
            controller.picture = old_picture
            controller.serve_file = old_serve_file

class TestPaginator:
    def check_paginator(self, params, output):
        """
        Helper method that instantiates a controller.Paginator object from the passed
        params and then checks that its attributes match the passed output.
        """
        count, num_pages, page_range = output
        paginator = controller.Paginator(*params)
        self.check_attribute('count', paginator, count, params)
        self.check_attribute('num_pages', paginator, num_pages, params)
        self.check_attribute('page_range', paginator, page_range, params)

    def check_attribute(self, name, paginator, expected, params):
        """
        Helper method that checks a single attribute and gives a nice error
        message upon test failure.
        """
        got = getattr(paginator, name)
        assert_equal(expected, got,
            "For '%s', expected %s but got %s.  controller.Paginator parameters were: %s"
            % (name, expected, got, params))

    def test_paginator(self):
        """
        Tests the paginator attributes using varying inputs.
        """
        nine = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        ten = nine + [10]
        eleven = ten + [11]
        tests = (
            # Each item is two tuples:
            #     First tuple is controller.Paginator parameters - object_list, per_page,
            #         orphans, and allow_empty_first_page.
            #     Second tuple is resulting controller.Paginator attributes - count,
            #         num_pages, and page_range.
            # Ten items, varying orphans, no empty first page.
            ((ten, 4, 0, False), (10, 3, [1, 2, 3])),
            ((ten, 4, 1, False), (10, 3, [1, 2, 3])),
            ((ten, 4, 2, False), (10, 2, [1, 2])),
            ((ten, 4, 5, False), (10, 2, [1, 2])),
            ((ten, 4, 6, False), (10, 1, [1])),
            # Ten items, varying orphans, allow empty first page.
            ((ten, 4, 0, True), (10, 3, [1, 2, 3])),
            ((ten, 4, 1, True), (10, 3, [1, 2, 3])),
            ((ten, 4, 2, True), (10, 2, [1, 2])),
            ((ten, 4, 5, True), (10, 2, [1, 2])),
            ((ten, 4, 6, True), (10, 1, [1])),
            # One item, varying orphans, no empty first page.
            (([1], 4, 0, False), (1, 1, [1])),
            (([1], 4, 1, False), (1, 1, [1])),
            (([1], 4, 2, False), (1, 1, [1])),
            # One item, varying orphans, allow empty first page.
            (([1], 4, 0, True), (1, 1, [1])),
            (([1], 4, 1, True), (1, 1, [1])),
            (([1], 4, 2, True), (1, 1, [1])),
            # Zero items, varying orphans, no empty first page.
            (([], 4, 0, False), (0, 0, [])),
            (([], 4, 1, False), (0, 0, [])),
            (([], 4, 2, False), (0, 0, [])),
            # Zero items, varying orphans, allow empty first page.
            (([], 4, 0, True), (0, 1, [1])),
            (([], 4, 1, True), (0, 1, [1])),
            (([], 4, 2, True), (0, 1, [1])),
            # Number if items one less than per_page.
            (([], 1, 0, True), (0, 1, [1])),
            (([], 1, 0, False), (0, 0, [])),
            (([1], 2, 0, True), (1, 1, [1])),
            ((nine, 10, 0, True), (9, 1, [1])),
            # Number if items equal to per_page.
            (([1], 1, 0, True), (1, 1, [1])),
            (([1, 2], 2, 0, True), (2, 1, [1])),
            ((ten, 10, 0, True), (10, 1, [1])),
            # Number if items one more than per_page.
            (([1, 2], 1, 0, True), (2, 2, [1, 2])),
            (([1, 2, 3], 2, 0, True), (3, 2, [1, 2])),
            ((eleven, 10, 0, True), (11, 2, [1, 2])),
            # Number if items one more than per_page with one orphan.
            (([1, 2], 1, 1, True), (2, 1, [1])),
            (([1, 2, 3], 2, 1, True), (3, 1, [1])),
            ((eleven, 10, 1, True), (11, 1, [1])),
        )
        for params, output in tests:
            self.check_paginator(params, output)

    def check_indexes(self, params, page_num, indexes):
        """
        Helper method that instantiates a controller.Paginator object from the passed
        params and then checks that the start and end indexes of the passed
        page_num match those given as a 2-tuple in indexes.
        """
        paginator = controller.Paginator(*params)
        if page_num == 'first':
            page_num = 1
        elif page_num == 'last':
            page_num = paginator.num_pages
        page = paginator.page(page_num)
        start, end = indexes
        msg = ("For %s of page %s, expected %s but got %s."
               " controller.Paginator parameters were: %s")
        assert_equal(start, page.start_index(),
            msg % ('start index', page_num, start, page.start_index(), params))
        assert_equal(end, page.end_index(),
            msg % ('end index', page_num, end, page.end_index(), params))

    def test_page_indexes(self):
        """
        Tests that paginator pages have the correct start and end indexes.
        """
        ten = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        tests = (
            # Each item is three tuples:
            #     First tuple is controller.Paginator parameters - object_list, per_page,
            #         orphans, and allow_empty_first_page.
            #     Second tuple is the start and end indexes of the first page.
            #     Third tuple is the start and end indexes of the last page.
            # Ten items, varying per_page, no orphans.
            ((ten, 1, 0, True), (1, 1), (10, 10)),
            ((ten, 2, 0, True), (1, 2), (9, 10)),
            ((ten, 3, 0, True), (1, 3), (10, 10)),
            ((ten, 5, 0, True), (1, 5), (6, 10)),
            # Ten items, varying per_page, with orphans.
            ((ten, 1, 1, True), (1, 1), (9, 10)),
            ((ten, 1, 2, True), (1, 1), (8, 10)),
            ((ten, 3, 1, True), (1, 3), (7, 10)),
            ((ten, 3, 2, True), (1, 3), (7, 10)),
            ((ten, 3, 4, True), (1, 3), (4, 10)),
            ((ten, 5, 1, True), (1, 5), (6, 10)),
            ((ten, 5, 2, True), (1, 5), (6, 10)),
            ((ten, 5, 5, True), (1, 10), (1, 10)),
            # One item, varying orphans, no empty first page.
            (([1], 4, 0, False), (1, 1), (1, 1)),
            (([1], 4, 1, False), (1, 1), (1, 1)),
            (([1], 4, 2, False), (1, 1), (1, 1)),
            # One item, varying orphans, allow empty first page.
            (([1], 4, 0, True), (1, 1), (1, 1)),
            (([1], 4, 1, True), (1, 1), (1, 1)),
            (([1], 4, 2, True), (1, 1), (1, 1)),
            # Zero items, varying orphans, allow empty first page.
            (([], 4, 0, True), (0, 0), (0, 0)),
            (([], 4, 1, True), (0, 0), (0, 0)),
            (([], 4, 2, True), (0, 0), (0, 0)),
        )
        for params, first, last in tests:
            self.check_indexes(params, 'first', first)
            self.check_indexes(params, 'last', last)
        # When no items and no empty first page, we should get controller.EmptyPage error.
        assert_raises(controller.EmptyPage, self.check_indexes, ([], 4, 0, False), 1, None)
        assert_raises(controller.EmptyPage, self.check_indexes, ([], 4, 1, False), 1, None)
        assert_raises(controller.EmptyPage, self.check_indexes, ([], 4, 2, False), 1, None)

    def test_representation(self):
        class PaginatorStub:
            num_pages = 10

        page = controller.Page([], 2, PaginatorStub)
        assert_equal('<Page 2 of 10>', repr(page))

    def test_has_next_true(self):
        class PaginatorStub:
            num_pages = 10

        page = controller.Page([], 2, PaginatorStub)
        message = '%s should have next page, since is the page 2 of 10' % page
        assert page.has_next(), message

    def test_has_next_false(self):
        class PaginatorStub:
            num_pages = 2

        page = controller.Page([], 2, PaginatorStub)
        message = '%s should not have next page, since is the page 2 of 2' % page
        assert not page.has_next(), message

    def test_has_previous_true(self):
        class PaginatorStub:
            num_pages = 10

        page = controller.Page([], 2, PaginatorStub)
        message = '%s should have previous page, since is the page 2' % page
        assert page.has_previous(), message

    def test_has_previous_false(self):
        class PaginatorStub:
            num_pages = 2

        page = controller.Page([], 1, PaginatorStub)
        message = '%s should not have previous page, since is the page 1' % page
        assert not page.has_previous(), message

    def test_has_other_pages_true_1of2(self):
        class PaginatorStub:
            num_pages = 2

        page = controller.Page([], 1, PaginatorStub)
        message = '%s should have other pages' % page
        assert page.has_other_pages(), message

    def test_has_other_pages_true_2of2(self):
        class PaginatorStub:
            num_pages = 2

        page = controller.Page([], 2, PaginatorStub)
        message = '%s should have other pages' % page
        assert page.has_other_pages(), message

    def test_has_other_pages_true_2of3(self):
        class PaginatorStub:
            num_pages = 3

        page = controller.Page([], 2, PaginatorStub)
        message = '%s should have other pages' % page
        assert page.has_other_pages(), message

    def test_has_other_pages_true_3of3(self):
        class PaginatorStub:
            num_pages = 3

        page = controller.Page([], 3, PaginatorStub)
        message = '%s should have other pages' % page
        assert page.has_other_pages(), message

    def test_has_other_pages_false(self):
        class PaginatorStub:
            num_pages = 1

        page = controller.Page([], 1, PaginatorStub)
        message = '%s should not have other pages' % page
        assert not page.has_other_pages(), message

    def test_next_page_number(self):
        class PaginatorStub:
            num_pages = 2

        page = controller.Page([], 1, PaginatorStub)

        got = page.next_page_number()
        expected = 2

        message = "%s's next page number should be 2, got %r" % (page, got)
        assert got == expected, message

    def test_previous_page_number(self):
        class PaginatorStub:
            num_pages = 2

        page = controller.Page([], 2, PaginatorStub)

        got = page.previous_page_number()
        expected = 1

        message = "%s's previous page number should be 1, got %r" % (page, got)
        assert got == expected, message

    def test_page_validate_number_not_integer(self):
        p = controller.Paginator(range(5), 2)
        assert_raises(controller.PageNotAnInteger,
                      p.validate_number,
                      '1sda0')

    def test_page_validate_number_less_than_1(self):
        p = controller.Paginator(range(5), 2)
        assert_raises(controller.EmptyPage,
                      p.validate_number,
                      -1)

    def test_page_validate_number_when_not_allowing_1st_empty_page(self):
        p = controller.Paginator([], 2,
                                 allow_empty_first_page=False)
        assert_raises(controller.EmptyPage,
                      p.validate_number,
                      1)

