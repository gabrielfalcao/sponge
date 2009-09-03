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
from nose.tools import assert_equals
from utils import assert_raises
from sponge.helpers import pagination, slugify

class TestPaginator:
    def check_paginator(self, params, output):
        """
        Helper method that instantiates a pagination.Paginator object from the passed
        params and then checks that its attributes match the passed output.
        """
        count, num_pages, page_range = output
        paginator = pagination.Paginator(*params)
        self.check_attribute('count', paginator, count, params)
        self.check_attribute('num_pages', paginator, num_pages, params)
        self.check_attribute('page_range', paginator, page_range, params)

    def check_attribute(self, name, paginator, expected, params):
        """
        Helper method that checks a single attribute and gives a nice error
        message upon test failure.
        """
        got = getattr(paginator, name)
        assert_equals(expected, got,
            "For '%s', expected %s but got %s.  pagination.Paginator parameters were: %s"
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
            #     First tuple is pagination.Paginator parameters - object_list, per_page,
            #         orphans, and allow_empty_first_page.
            #     Second tuple is resulting pagination.Paginator attributes - count,
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
        Helper method that instantiates a pagination.Paginator object from the passed
        params and then checks that the start and end indexes of the passed
        page_num match those given as a 2-tuple in indexes.
        """
        paginator = pagination.Paginator(*params)
        if page_num == 'first':
            page_num = 1
        elif page_num == 'last':
            page_num = paginator.num_pages
        page = paginator.page(page_num)
        start, end = indexes
        msg = ("For %s of page %s, expected %s but got %s."
               " pagination.Paginator parameters were: %s")
        assert_equals(start, page.start_index(),
            msg % ('start index', page_num, start, page.start_index(), params))
        assert_equals(end, page.end_index(),
            msg % ('end index', page_num, end, page.end_index(), params))

    def test_page_indexes(self):
        """
        Tests that paginator pages have the correct start and end indexes.
        """
        ten = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        tests = (
            # Each item is three tuples:
            #     First tuple is pagination.Paginator parameters - object_list, per_page,
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
        # When no items and no empty first page, we should get pagination.EmptyPage error.
        assert_raises(pagination.EmptyPage, self.check_indexes, ([], 4, 0, False), 1, None)
        assert_raises(pagination.EmptyPage, self.check_indexes, ([], 4, 1, False), 1, None)
        assert_raises(pagination.EmptyPage, self.check_indexes, ([], 4, 2, False), 1, None)

    def test_representation(self):
        class PaginatorStub:
            num_pages = 10

        page = pagination.Page([], 2, PaginatorStub)
        assert_equals('<Page 2 of 10>', repr(page))

    def test_has_next_true(self):
        class PaginatorStub:
            num_pages = 10

        page = pagination.Page([], 2, PaginatorStub)
        message = '%s should have next page, since is the page 2 of 10' % page
        assert page.has_next(), message

    def test_has_next_false(self):
        class PaginatorStub:
            num_pages = 2

        page = pagination.Page([], 2, PaginatorStub)
        message = '%s should not have next page, since is the page 2 of 2' % page
        assert not page.has_next(), message

    def test_has_previous_true(self):
        class PaginatorStub:
            num_pages = 10

        page = pagination.Page([], 2, PaginatorStub)
        message = '%s should have previous page, since is the page 2' % page
        assert page.has_previous(), message

    def test_has_previous_false(self):
        class PaginatorStub:
            num_pages = 2

        page = pagination.Page([], 1, PaginatorStub)
        message = '%s should not have previous page, since is the page 1' % page
        assert not page.has_previous(), message

    def test_has_other_pages_true_1of2(self):
        class PaginatorStub:
            num_pages = 2

        page = pagination.Page([], 1, PaginatorStub)
        message = '%s should have other pages' % page
        assert page.has_other_pages(), message

    def test_has_other_pages_true_2of2(self):
        class PaginatorStub:
            num_pages = 2

        page = pagination.Page([], 2, PaginatorStub)
        message = '%s should have other pages' % page
        assert page.has_other_pages(), message

    def test_has_other_pages_true_2of3(self):
        class PaginatorStub:
            num_pages = 3

        page = pagination.Page([], 2, PaginatorStub)
        message = '%s should have other pages' % page
        assert page.has_other_pages(), message

    def test_has_other_pages_true_3of3(self):
        class PaginatorStub:
            num_pages = 3

        page = pagination.Page([], 3, PaginatorStub)
        message = '%s should have other pages' % page
        assert page.has_other_pages(), message

    def test_has_other_pages_false(self):
        class PaginatorStub:
            num_pages = 1

        page = pagination.Page([], 1, PaginatorStub)
        message = '%s should not have other pages' % page
        assert not page.has_other_pages(), message

    def test_next_page_number(self):
        class PaginatorStub:
            num_pages = 2

        page = pagination.Page([], 1, PaginatorStub)

        got = page.next_page_number()
        expected = 2

        message = "%s's next page number should be 2, got %r" % (page, got)
        assert got == expected, message

    def test_previous_page_number(self):
        class PaginatorStub:
            num_pages = 2

        page = pagination.Page([], 2, PaginatorStub)

        got = page.previous_page_number()
        expected = 1

        message = "%s's previous page number should be 1, got %r" % (page, got)
        assert got == expected, message

    def test_page_validate_number_not_integer(self):
        p = pagination.Paginator(range(5), 2)
        assert_raises(pagination.PageNotAnInteger,
                      p.validate_number,
                      '1sda0')

    def test_page_validate_number_less_than_1(self):
        p = pagination.Paginator(range(5), 2)
        assert_raises(pagination.EmptyPage,
                      p.validate_number,
                      -1)

    def test_page_validate_number_when_not_allowing_1st_empty_page(self):
        p = pagination.Paginator([], 2,
                                 allow_empty_first_page=False)
        assert_raises(pagination.EmptyPage,
                      p.validate_number,
                      1)

class TestSlugify:
    def test_simple_spaces(self):
        "slugify should replace blank spaces with a dash"
        original = "simple string with spaces"
        assert_equals(slugify(original),
                      "simple-string-with-spaces")

    def test_special_chars(self):
        "slugify should remove any special chars"
        original = "here!@#$%*-()_+and{}[]-~^`'´/?\|there"
        got = slugify(original)
        assert_equals(got, "here-and-there")

    def test_my_name(self):
        "slugify should be able to slugify my name :)"
        original = "Gabriel Falcão"
        got = slugify(original)
        assert_equals(got, "gabriel-falcao")

    def test_full_accents(self):
        "slugify should be able to slugify a much accented sentence"
        original = "Ação é bordô à síri tãmisa"
        got = slugify(original)
        assert_equals(got, "acao-e-bordo-a-siri-tamisa")
