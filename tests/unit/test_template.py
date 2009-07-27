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

from sponge import template

def test_template_has_make_url_function():
    assert hasattr(template, 'make_url'), 'sponge.template should have the function make_url'
    assert callable(template.make_url), 'sponge.template.make_url should be callable'

def test_make_url_takes_string_as_param():
    expected = r'sponge.template.make_url ' \
               'takes a string as param, got None.'
    assert_raises(TypeError, template.make_url, None, exc_pattern=expected)

def test_make_url_without_trailling_slash():
    base_url = 'http://my.unit.test/for/ma-cherie'
    cherrypy.request.base = base_url

    expected_url = 'http://my.unit.test/for/ma-cherie/index'
    got_url = template.make_url('index')
    assert got_url == expected_url, 'Expected %s, got %s' % (expected_url, got_url)

def test_make_url_with_trailling_slash_on_base_url():
    base_url = 'http://my.unit.test/for/ma-cherie/'
    cherrypy.request.base = base_url

    expected_url = 'http://my.unit.test/for/ma-cherie/index'
    got_url = template.make_url('index')
    assert got_url == expected_url, 'Expected %s, got %s' % (expected_url, got_url)

def test_make_url_with_trailling_slash_on_url_part():
    base_url = 'http://my.unit.test/for/ma-cherie'
    cherrypy.request.base = base_url

    expected_url = 'http://my.unit.test/for/ma-cherie/index'
    got_url = template.make_url('/index')
    assert got_url == expected_url, 'Expected %s, got %s' % (expected_url, got_url)

def test_make_url_with_trailling_slash_on_both():
    base_url = 'http://my.unit.test/for/ma-cherie/'
    cherrypy.request.base = base_url

    expected_url = 'http://my.unit.test/for/ma-cherie/index'
    got_url = template.make_url('/index')
    assert got_url == expected_url, 'Expected %s, got %s' % (expected_url, got_url)

def test_template_has_function_render_html():
    assert hasattr(template, 'render_html'), 'sponge.template should have the function render_html'
    assert callable(template.render_html), 'sponge.template.render_html should be callable'

def test_templates_render_html_raises_filename_nonstring():
    assert_raises(TypeError,
                  template.render_html,
                  None,
                  {},
                  exc_pattern=r'sponge.template.render_html ' \
                  'takes a string as filename param, got None.')
    assert_raises(TypeError,
                  template.render_html,
                  5,
                  {},
                  exc_pattern=r'sponge.template.render_html ' \
                  'takes a string as filename param, got 5.')

def test_templates_render_html_raises_filename_empty():
    assert_raises(TypeError,
                  template.render_html,
                  '',
                  {},
                  exc_pattern=r'sponge.template.render_html ' \
                  'filename param can not be empty.')

def test_templates_render_html_raises_context_nondict():
    assert_raises(TypeError,
                  template.render_html,
                  'index.html',
                  'a string',
                  exc_pattern=r'sponge.template.render_html ' \
                  'takes a dict as context param, got \'a string\'.')
    assert_raises(TypeError,
                  template.render_html,
                  'index.html',
                  5,
                  exc_pattern=r'sponge.template.render_html ' \
                  'takes a dict as context param, got 5.')

def test_templates_render_html_raises_context_already_have_make_url():
    assert_raises(KeyError,
                  template.render_html,
                  'index.html',
                  {'make_url': "ss"},
                  exc_pattern=r'The key "make_url" is already in ' \
                  'template context as[:] %s' % re.escape(repr(template.make_url)))
