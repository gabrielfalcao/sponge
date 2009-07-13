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
from Cheetah.Template import Template

#from sponge import __version__ as version
version = "FAKE"

class ProjectFolderExistsError(ValueError):
    pass

class Bob(object):
    '''Sponge Bob is the responsible for managing the user's application and its modules.'''

    ProjectFolderExists = ProjectFolderExistsError

    def __init__(self, parser=None, fs=None):
        self.parser = parser
        if not self.parser:
            import optparse
            usage = "\n>>> " + Bob.__doc__ + " <<<\n\nTo use type %prog [options]" \
                                             " or %prog -h (--help) for help with" \
                                             " the available options"
            self.parser = optparse.OptionParser(usage=usage, description=__doc__, version=version)

        self.fs = fs
        if not self.fs:
            from file_system import FileSystem
            self.fs = FileSystem()

    def run(self):
        options, args = self.parser.parse_args()

        if args and args[0] == 'create':
            self.create_project(options, args[1])
            return 0

        return 0

    def create_project(self, options, project_name):
        path = self.fs.abspath(self.fs.join(options.project_dir, project_name))
        if self.fs.exists(path):
            raise self.ProjectFolderExists("There is a folder at '%s' already, thus making it impossible to create a project there." % path)

        self.fs.mkdir(path)
        self.create_project_structure(options, project_name, path)

    def create_project_structure(self, options, project_name, project_path):
        template_folder = self.fs.abspath(self.fs.join(self.fs.dirname(self.get_file_path()), "templates", "create_project"))

        for f in self.fs.locate(path=template_folder, match="*.*", recursive=True):
            new_path = self.fs.rebase(path=f, origin_folder=template_folder, destiny_folder=project_path)
            t = Template(self.fs.read_all(path=f, encoding='utf-8'), searchList=[])
            self.fs.write_all(path=new_path, contents=str(t), encoding='utf-8', create_dir=True)

    def get_file_path(self):
        return __file__

if __name__ == "__main__":
    bob = Bob()
    sys.exit(bob.run())
