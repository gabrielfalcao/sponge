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

from setuptools import setup, find_packages
from sponge import __version__

setup(name='Sponge',
    version=__version__,
    description='A web framework aiming to get things dry, ' \
                'built on top of CherryPy and Genshi',
    author='Gabriel Falcao',
    author_email='gabriel@nacaolivre.org',
    url='http://gnu.gabrielfalcao.com/sponge',
    entry_points={
        'console_scripts': [
            'bob = sponge.bob:run',
        ]
    },
    packages=find_packages(),
    include_package_data = True,
    package_data = {
        'sponge': ['data/project.zip'],
    },
)
