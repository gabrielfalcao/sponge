#!/usr/bin/env python
# -*- coding: utf-8 -*-
# <Sponge - Lightweight Web Framework>
# Copyright (C) 2009 Gabriel Falcão <gabriel@nacaolivre.org>
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
import string

def slugify(s):
    s = s.decode('utf-8')
    entities = {}
    newstring = u""

    avoid = string.punctuation
    avoid = avoid.replace('-', u'´')
    for x in avoid:
        s = s.replace(x, '')

    entities[u'-'] = '-'
    entities[u' '] = '-'
    entities[u'À'] = 'a'
    entities[u'Á'] = 'a'
    entities[u'Â'] = 'a'
    entities[u'Ã'] = 'a'
    entities[u'Ä'] = 'a'
    entities[u'Å'] = 'a'
    entities[u'Æ'] = 'a'
    entities[u'Ç'] = 'c'
    entities[u'È'] = 'e'
    entities[u'É'] = 'e'
    entities[u'Ê'] = 'e'
    entities[u'Ë'] = 'e'
    entities[u'Ì'] = 'i'
    entities[u'Í'] = 'i'
    entities[u'Î'] = 'i'
    entities[u'Ï'] = 'i'
    entities[u'Ð'] = 'e'
    entities[u'Ò'] = 'o'
    entities[u'Ó'] = 'o'
    entities[u'Ô'] = 'o'
    entities[u'Õ'] = 'o'
    entities[u'Ö'] = 'o'
    entities[u'Ø'] = 'o'
    entities[u'Ù'] = 'u'
    entities[u'Ú'] = 'u'
    entities[u'Û'] = 'u'
    entities[u'Ü'] = 'u'
    entities[u'à'] = 'a'
    entities[u'á'] = 'a'
    entities[u'â'] = 'a'
    entities[u'ã'] = 'a'
    entities[u'ä'] = 'a'
    entities[u'å'] = 'a'
    entities[u'æ'] = 'a'
    entities[u'ç'] = 'c'
    entities[u'è'] = 'e'
    entities[u'é'] = 'e'
    entities[u'ê'] = 'e'
    entities[u'ë'] = 'e'
    entities[u'ì'] = 'i'
    entities[u'í'] = 'i'
    entities[u'î'] = 'i'
    entities[u'ï'] = 'i'
    entities[u'ò'] = 'o'
    entities[u'ó'] = 'o'
    entities[u'ô'] = 'o'
    entities[u'õ'] = 'o'
    entities[u'ö'] = 'o'
    entities[u'ø'] = 'o'
    entities[u'ù'] = 'u'
    entities[u'ú'] = 'u'
    entities[u'û'] = 'u'
    entities[u'ü'] = 'u'

    for letter in s:
        if letter in entities:
            newstring += entities[letter]
        else:
            newstring += letter
    return newstring.lower()
