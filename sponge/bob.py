#!/usr/bin/env python
# -*- coding: utf-8; -*-
#
# Copyright (C) 2009 Gabriel Falcão <gabriel@nacaolivre.org>
# Copyright (C) 2009 Bernardo Heynemann <heynemann@gmail.com>
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

import sys
import os

#from sponge import __version__ as version
version = "FAKE"

class Bob(object):
    '''Sponge Bob is the responsible for managing the user's application and its modules.'''

    def __init__(self, parser=None):
        self.parser = parser
        if not self.parser:
            import optparse
            usage = "\n>>> " + Bob.__doc__ + " <<<\n\nTo use type %prog [options]" \
                                             " or %prog -h (--help) for help with" \
                                             " the available options"
            self.parser = optparse.OptionParser(usage=usage, description=__doc__, version=version)

    def run(self):
        options, args = self.parser.parse_args()

        if args and args[0] == 'create':
            self.create_project(options, args[1])
        return 0

    def create_project(self, options, project_name):
        pass

if __name__ == "__main__":
    bob = Bob()
    sys.exit(bob.run())
