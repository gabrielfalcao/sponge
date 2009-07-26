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

import os
import sys
import codecs
import cherrypy
import nose
from sponge import __version__ as version
from sponge.core import ConfigValidator, SpongeConfig
from sponge.core.io import FileSystem
from sponge.data import SpongeData

basic_config = {
    'run-as': 'wsgi',
    'host': '0.0.0.0',
    'port': 4000,
    'autoreload': True,
    'application': {
        'classes': {
            'HelloWorldController': '/'
        },
        'image-dir': None,
        'path': None,
        'template-dir': None,
        'static': {
            '/media': None,
        },
    },
}

class Bob(object):
    """Sponge Bob is the responsible for managing
    the user's application and its modules."""

    def __init__(self, parser=None, fs=None):
        self.parser = parser
        if not self.parser:
            import optparse
            usage = "\n>>> %s <<<\n\nTo use type %%prog [options]" \
                    " or %%prog -h (--help) for help with" \
                    " the available options" % self.__doc__
            self.parser = optparse.OptionParser(usage=usage,
                                                description=__doc__,
                                                version=version)
        self.fs = fs
        if not self.fs:
            self.fs = FileSystem()

    def run(self):
        options, args = self.parser.parse_args()
        error_msg = '\nBob got a error when %s.\n    %s\n'

        accepted = 'create', 'go', 'test', 'start'
        if not args:
            msg = '\nmissing argument, choose one in %s\n'
            sys.stderr.write(msg % ", ".join(accepted))

        if args[0] not in accepted:
            msg = '\n%s is an invalid argument, choose one in %s\n'
            sys.stderr.write(msg % (args[0], ", ".join(accepted)))

        return getattr(self, args[0])(*args[1:])

    def configure(self):
        import yaml
        current_full_path = self.fs.current_dir()

        full_path = self.fs.current_dir("settings.yml")
        raw_yaml = codecs.open(full_path, 'r', 'utf-8').read()
        orig_dict = yaml.load(raw_yaml)

        validator = ConfigValidator(orig_dict)
        config = SpongeConfig(cherrypy.config, validator)
        config.setup_all(current_full_path)

    def go(self):
        self.configure()
        cherrypy.quickstart()

    def test(self):
        self.configure()
        for fullpath in self.fs.locate('tests', '__init__.py'):
            path = os.path.dirname(fullpath).rstrip(os.sep)
            self.fs.pushd(path)
            module = path.split(os.sep)[-1]
            try:
                nose.runmodule(module)
            except SystemExit:
                pass

            self.fs.popd()

    def create(self, project_name=None):
        import syck as yaml
        if not project_name:
            error_msg = 'missing project name, try ' \
                        'something like "bob create foobar"'
            sys.stderr.write("\n%s\n" % error_msg)
            raise SystemExit(1)

        path = self.fs.current_dir(project_name)

        if self.fs.exists(path):
            error_msg = 'The path "%s" already exists. ' \
                        'Maybe you could choose another ' \
                        'name for your project ?' % path

            sys.stderr.write("\n%s\n" % error_msg)
        self.fs.mkdir(path)

        cfg = self.fs.open(self.fs.join(path, 'settings.yml'), 'w')
        cdict = basic_config.copy()
        media_path = self.fs.join(path, 'media')
        cdict['application']['static']['/media'] = media_path

        controller_path = self.fs.join(path, 'app', 'controllers.py')
        cdict['application']['path'] = controller_path

        image_path = self.fs.join(path, 'media', 'img')
        cdict['application']['image-dir'] = image_path

        template_path = self.fs.join(path, 'templates')
        cdict['application']['template-dir'] = template_path

        cfg.write(yaml.dump(cdict))
        cfg.close()

        zip_file = SpongeData.get_file('project.zip')
        self.fs.extract_zip(zip_file, path)

    def start(self, project_name=None):
        self.create(project_name)
        self.fs.pushd(project_name)
        self.go()

    def get_file_path(self):
        return __file__

def run(*args, **kw):
    bob = Bob(*args, **kw)
    sys.exit(bob.run())
