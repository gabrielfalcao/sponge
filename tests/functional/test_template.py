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
import os
import cherrypy
from sponge import template
from utils import assert_raises

templates = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))

def test_render_html_param_filename_takes_string():
    assert_raises(TypeError, template.render_html, None, None,
                  exc_pattern=r'sponge.template.render_html ' \
                  'takes a string as filename param, got None.')
    assert_raises(TypeError, template.render_html, 5, None,
                  exc_pattern=r'sponge.template.render_html ' \
                  'takes a string as filename param, got 5.')

def test_render_html_param_filename_should_not_be_empty():
    assert_raises(TypeError, template.render_html, '', None,
                  exc_pattern=r'sponge.template.render_html ' \
                  'filename param can not be empty.')

def test_render_html_complains_cherrypy_not_configured_when_no_template_path_specified():
    assert_raises(LookupError, template.render_html, 'index.html', {},
                  exc_pattern=r'You must configure "template.dir" ' \
                  'string in CherryPy or pass template_path param ' \
                  'to render_html')

def test_render_html_param_template_path_takes_string():
    assert_raises(TypeError, template.render_html, 'index.html', {},
                  template_path=1,
                  exc_pattern=r'sponge.template.render_html ' \
                  'takes a string as template_path param, got 1.')
    assert_raises(TypeError, template.render_html, 'index.html', {},
                  template_path={},
                  exc_pattern=r'sponge.template.render_html ' \
                  'takes a string as template_path param, got {}.')

def test_render_html_param_template_path_takes_string():
    assert_raises(TypeError, template.render_html, 'index.html', {},
                  template_path=1,
                  exc_pattern=r'sponge.template.render_html ' \
                  'takes a string as template_path param, got 1.')
    assert_raises(TypeError, template.render_html, 'index.html', {},
                  template_path={},
                  exc_pattern=r'sponge.template.render_html ' \
                  'takes a string as template_path param, got {}.')

def test_render_html():
    got = template.render_html('test1.html', dict(title='foo', header='bar'), template_path=templates)
    assert '<title>My title: foo</title>' in got
    assert '<h1>My header: bar</h1>' in got
