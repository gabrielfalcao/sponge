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
import Image
import ImageDraw
import cherrypy
import StringIO

from genshi.template import TemplateLoader

def make_url(url):
    if not isinstance(url, basestring):
        raise TypeError('sponge.view.make_url ' \
                        'takes a string as param, got %r.' % url)
    if url.startswith('/'):
        url = url[1:]

    base = cherrypy.request.base
    if base.endswith('/'):
        base = base[:-1]

    return "%s/%s" % (base, url)

def render_html(filename, context, template_path=None):
    if not isinstance(filename, basestring):
        raise TypeError('sponge.view.render_html ' \
                        'takes a string as filename param, got %r.' % filename)

    if not len(filename):
        raise TypeError('sponge.view.render_html ' \
                        'filename param can not be empty.')

    if not isinstance(context, dict):
        raise TypeError('sponge.view.render_html ' \
                        'takes a dict as context param, got %r.' % context)

    if 'make_url' in context.keys():
        msg = 'The key "make_url" is already in ' \
              'template context as: %r' % make_url
        raise KeyError(msg)

    if template_path is None:
        try:
            template_path = cherrypy.config['view.dir']
        except KeyError:
            raise LookupError('You must configure "view.dir" string in ' \
                              'CherryPy or pass template_path param to render_html')


    elif not isinstance(template_path, basestring):
        raise TypeError('sponge.view.render_html ' \
                        'takes a string as template_path param, got %r.' % template_path)

    context['make_url'] = make_url
    loader = TemplateLoader(template_path,
                            auto_reload=True)
    template = loader.load(filename)
    generator = template.generate(**context)
    return generator.render('html', doctype='html')



def jpeg(path, base_path=None):
    if not isinstance(path, basestring):
        raise TypeError('jpeg() takes a string as parameter, got %r.' % path)
    fullpath = os.path.join(base_path, path)
    try:
        img = Image.open(fullpath)
    except IOError, e:
        cherrypy.response.status = 404
        return unicode(e)

    if not base_path:
        base_path = cherrypy.config['image.dir']

    sfile = StringIO.StringIO()
    img.save(sfile, "JPEG", quality=100)
    cherrypy.response.headers['Content-type'] = "image/jpeg"
    return sfile.getvalue()

# Based in the original, public license, version from Kevin Cazabon
# <http://www.cazabon.com/python/>

def crop_to_fit(img, output_size):
    live_area = (0, 0, img.size[0] - 1, img.size[1] - 1)
    live_size = (live_area[2] - live_area[0], live_area[3] - live_area[1])

    # calculate the aspect ratio of the live_area
    live_area_aspect_ratio = float(live_size[0])/float(live_size[1])

    # calculate the aspect ratio of the output image
    aspect_ratio = float(output_size[0])/float(output_size[1])

    # figure out if the sides or top/bottom will be cropped off
    if live_area_aspect_ratio >= aspect_ratio:
        # live_area is wider than what's needed, crop the sides
        crop_width = int((aspect_ratio * float(live_size[1])) + 0.5)
        crop_height = live_size[1]

    # make the crop
    left_side = int(live_area[0] + (float(live_size[0] - crop_width) * 0.5))
    top_side = int(live_area[1] + (float(live_size[1] - crop_height) * 0.5))


    outputImage = img.crop((left_side, top_side, left_side + crop_width, top_side + crop_height))

    # resize the image and return it
    return outputImage.resize(output_size, 3)

def picture(path,
            width,
            height,
            crop=True,
            center=True,
            mask=None,
            background=0xffffff,
            base_path=None):

    if not isinstance(path, basestring):
        raise TypeError('picture() takes a string as path parameter, got %r.' % path)

    if not isinstance(width, int):
        raise TypeError('picture() takes a integer as width parameter, got %r.' % width)

    if not isinstance(height, int):
        raise TypeError('picture() takes a integer as height parameter, got %r.' % height)

    if not base_path:
        base_path = cherrypy.config['image.dir']

    wished_size = width, height
    img = Image.open(os.path.join(base_path, path))

    if crop:
        img = crop_to_fit(img, (width, height))

    if center:
        old_img = img
        img = Image.new('RGBA', (width, height), background)
        ow, oh = old_img.size
        left = (width - ow) / 2
        top = (height - oh) / 2
        img.paste(old_img, (left, top))

    if mask:
        mask_img = Image.open(mask)
        img.paste(mask_img, None, mask_img)

    sfile = StringIO.StringIO()
    img.save(sfile, "JPEG", quality=100)
    cherrypy.response.headers['Content-type'] = "image/jpeg"
    return sfile.getvalue()
