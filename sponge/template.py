#!/usr/bin/env python
# -*- coding: utf-8 -*-
# <Sponge - Lightweight Web Framework>
# Copyright (C) 2009 Gabriel Falcão <gabriel@nacaolivre.org>
# Copyright (C) 2009 Bernardo Heynemann <heynemann@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import cherrypy
from genshi.template import TemplateLoader

def make_url(url):
    if not isinstance(url, basestring):
        raise TypeError('sponge.template.make_url ' \
                        'takes a string as param, got %r.' % url)
    if url.startswith('/'):
        url = url[1:]

    base = cherrypy.request.base
    if base.endswith('/'):
        base = base[:-1]

    return "%s/%s" % (base, url)

def render_html(filename, context=None, template_path=None):
    if context is None:
        context = {}

    if not isinstance(filename, basestring):
        raise TypeError('sponge.template.render_html ' \
                        'takes a string as filename param, got %r.' % filename)

    if not len(filename):
        raise TypeError('sponge.template.render_html ' \
                        'filename param can not be empty.')

    if not isinstance(context, dict):
        raise TypeError('sponge.template.render_html ' \
                        'takes a dict as context param, got %r.' % context)

    if 'make_url' in context.keys():
        msg = 'The key "make_url" is already in ' \
              'template context as: %r' % make_url
        raise KeyError(msg)

    if template_path is None:
        try:
            template_path = cherrypy.config['template.dir']
        except KeyError:
            raise LookupError('You must configure "template.dir" string in ' \
                              'CherryPy or pass template_path param to render_html')

    elif not isinstance(template_path, basestring):
        raise TypeError('sponge.template.render_html ' \
                        'takes a string as template_path param, got %r.' % template_path)

    context['make_url'] = make_url
    loader = TemplateLoader(template_path,
                            auto_reload=True)
    template = loader.load(filename)
    generator = template.generate(**context)
    return generator.render('html', doctype='html')

