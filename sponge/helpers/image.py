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

import os
import Image
import ImageDraw
import cherrypy
import StringIO

def jpeg(path, base_path=None):
    if not isinstance(path, basestring):
        raise TypeError('jpeg() takes a string as parameter, got %r.' % path)

    if not base_path:
        base_path = cherrypy.config['image.dir']

    fullpath = os.path.join(base_path, path)

    try:
        img = Image.open(fullpath)
    except IOError, e:
        cherrypy.response.status = 404
        return unicode(e)


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
    else:
        #live_area is taller than what's needed, crop the top and bottom
        crop_width = live_size[0]
        crop_height = int((float(live_size[0]) / aspect_ratio) + 0.5)

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

    sfile = StringIO.StringIO()
    img.save(sfile, "JPEG", quality=100)
    cherrypy.response.headers['Content-type'] = "image/jpeg"
    return sfile.getvalue()
