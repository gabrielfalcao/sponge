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

import re
import sys
import yaml
import cherrypy
import optparse

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
            'HelloWorldController': '/',
            'AjaxController': '/ajax',
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

    ACTIONS = [
        ('create', '<projectname> - creates a new project, which means creating a new folder in current directory, named projectname'),
        ('go', 'start the cherrypy server using the configuration file settings.yml in current directory.'),
        ('start', '<projectname> executes both bob create and bob go'),
    ]

    def __init__(self, parser=None, fs=None):
        self.parser = parser
        if not self.parser:
            self.parser = optparse.OptionParser(usage=self.get_help(),
                                                description=__doc__,
                                                version=version)
        self.fs = fs
        if not self.fs:
            self.fs = FileSystem()

    def get_help(self):
        actions = "\n".join(["%s %s" % (k, v) for k, v in self.ACTIONS])
        usage = "\n %s \n\nTo use type %%prog [options]" \
                " or %%prog -h (--help) for help with" \
                " the available options\n\nACTIONS:\n\n%s" % (self.__doc__, actions)

        return usage

    def exit(self, code=1):
        raise SystemExit(code)

    def run(self):
        accepted = [a[0] for a in self.ACTIONS]
        options, args = self.parser.parse_args()
        error_msg = '\nBob got a error when %s.\n    %s\n'

        if not args:
            msg = '\nmissing argument, choose one in %s\n'
            sys.stderr.write(msg % ", ".join(accepted))
            self.exit()

        if args[0] not in accepted:
            msg = '\n%s is an invalid argument, choose one in %s\n'
            sys.stderr.write(msg % (args[0], ", ".join(accepted)))
            self.exit()

        return getattr(self, args[0])(*args[1:])

    def configure(self):
        current_full_path = self.fs.current_dir()

        full_path = self.fs.current_dir("settings.yml")
        raw_yaml = self.fs.open(full_path, 'r').read()
        orig_dict = yaml.load(raw_yaml)

        validator = ConfigValidator(orig_dict)
        config = SpongeConfig(cherrypy.config, validator)
        config.setup_all(current_full_path)

    def go(self):
        self.configure()
        cherrypy.quickstart()

    def create(self, project_name=None):
        if not project_name:
            error_msg = 'missing project name, try ' \
                        'something like "bob create foobar"'
            sys.stderr.write("\n%s\n" % error_msg)
            self.exit()

        path = self.fs.current_dir(project_name)

        if self.fs.exists(path):
            error_msg = 'The path "%s" already exists. ' \
                        'Maybe you could choose another ' \
                        'name for your project ?' % path

            sys.stderr.write("\n%s\n" % error_msg)
            self.exit()

        self.fs.mkdir(path)

        cfg = self.fs.open(self.fs.join(path, 'settings.yml'), 'w')
        cdict = basic_config.copy()

        media_path = self.fs.join('media')
        cdict['application']['static']['/media'] = media_path

        controller_path = self.fs.join('app', 'controllers.py')
        cdict['application']['path'] = controller_path

        image_path = self.fs.join('media', 'img')
        cdict['application']['image-dir'] = image_path

        template_path = self.fs.join('templates')
        cdict['application']['template-dir'] = template_path

        yml_data = self.fix_yml(yaml.dump(cdict, indent=True))
        cfg.write(yml_data)
        cfg.close()

        zip_file = SpongeData.get_file('project.zip')
        self.fs.extract_zip(zip_file, path)

    def fix_yml(self, yml):
        yml = re.sub('[ ]+{', '{', yml)
        pattern1 = r'(?P<spc>[ ]+)(?P<pre>[^{]+)[{](?P<cnt>[^}]+)[}]'
        replacement1 = r'\g<spc>\g<pre>\n  \g<spc>\g<cnt>'
        yml = re.sub(pattern1, replacement1, yml)
        pattern2 = r'(?P<spc>[ ]+)(?P<pre>[^,]+)[,][ ]*'
        replacement2 = r'\g<spc>\g<pre>\n  \g<spc>'
        yml = re.sub(pattern2, replacement2, yml)
        return yml

    def start(self, project_name=None):
        self.create(project_name)
        self.fs.pushd(project_name)
        self.go()

    def get_file_path(self):
        return __file__

def run(*args, **kw):
    bob = Bob(*args, **kw)
    sys.exit(bob.run())
