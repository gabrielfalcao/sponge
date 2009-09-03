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
import re
import sys
import cherrypy

from sponge.core.io import FileSystem, ClassLoader

class InvalidValueError(Exception):
    pass

class RequiredOptionError(Exception):
    pass

class ConfigValidator(object):
    class AnyValue(object):
        def __init__(self, vartype):
            if not isinstance(vartype, type):
                raise TypeError, 'ConfigValidator.AnyValue takes a ' \
                  'type as parameter, got %s' % repr(vartype)
            self.vartype = vartype

    mandatory = [
        'run-as',
        'host',
        'port',
        'autoreload',
        'application',
    ]
    possible = {
        'run-as': ['standalone', 'wsgi'],
        'host': r'^\d{1,3}[.]\d{1,3}[.]\d{1,3}[.]\d{1,3}$',
        'port': r'^\d+$',
        'autoreload': AnyValue(bool),
        'application': {
            r'^[a-zA-Z_-][\w_-]*$': r'^[/].*$'
        },
        'static': {
            r'^[a-zA-Z/_-][\w_-]*$': r'^[/].*$'
        },
        'databases': {
            r'^[\w_-]+$': '^.+$'
        },
        'extra': AnyValue(dict)
    }

    def __init__(self, cdict):
        if not isinstance(cdict, dict):
            raise TypeError, \
                  'ConfigValidator takes a dict as parameter, got None.'
        self.cdict = cdict

    def validate(self):
        self.validate_mandatory()

    def raise_invalid(self, option, value):
        raise InvalidValueError, 'Invalid value in "%s" ' \
              'option: "%s". Read the Sponge documentation ' \
              'for more information.' % (option, value)

    def validate_mandatory(self):
        keys = self.cdict.keys()
        for option in self.possible:
            if option in self.mandatory and \
                option not in keys:
                raise RequiredOptionError, \
                      'You get to set "%s" option within settings.yml' \
                      % option
            if option not in self.cdict.keys():
                continue

            validator = self.possible[option]
            raw_value = self.cdict[option]
            value = unicode(raw_value)
            if isinstance(validator, list):
                if value not in validator:
                    self.raise_invalid(option, value)

            if isinstance(validator, basestring):
                if not re.match(validator, value):
                    self.raise_invalid(option, value)

            if isinstance(validator, self.AnyValue):
                if not isinstance(raw_value, validator.vartype):
                    self.raise_invalid(option, value)

            if isinstance(validator, dict):
                if not isinstance(raw_value, dict):
                    self.raise_invalid(option, value)
                self.validate_dict(option, validator, raw_value)

        return True

    def validate_dict(self, option, validator, dict_to_validate):
        for key_regex, value_regex in validator.items():
            for key, value in dict_to_validate.items():
                if isinstance(value, dict):
                    self.validate_dict(key, validator, value)

                elif isinstance(value, basestring):
                    if not re.match(key_regex, key):
                        self.raise_invalid(option, key)
                    if not re.match(value_regex, value):
                        self.raise_invalid(key, value)

                else:
                    self.raise_invalid(key, value)

class SpongeConfig(object):
    fs = FileSystem()

    def __init__(self, config_dict, validator):
        if not isinstance(config_dict, dict):
            raise TypeError, 'SpongeConfig parameter 1 must be a dict, ' \
                  'got %s.' % repr(config_dict)

        if not isinstance(validator, ConfigValidator):
            raise TypeError, 'SpongeConfig parameter 2 must be a ' \
                  'ConfigValidator, got %s.' % repr(validator)

        self.d = config_dict
        self.validator = validator

    def set_setting(self, key, value):
        self.d[key] = value

    def setup_all(self, current_full_path):
        sys.path.append(os.getcwd())
        if not isinstance(current_full_path, basestring):
            raise TypeError, 'SpongeConfig.setup_all takes a string, ' \
                  'got %s.' % repr(current_full_path)

        if not os.path.isabs(current_full_path):
            raise TypeError, 'SpongeConfig.setup_all takes a absolute ' \
                  'path, got %s.' % current_full_path

        cdict = self.validator.cdict
        sponge_root = self.fs.abspath(current_full_path)
        self.set_setting('server.socket_port', int(cdict['port']))
        self.set_setting('server.socket_host', cdict['host'])
        self.set_setting('tools.sessions.on', True)
        self.set_setting('tools.sessions.timeout', 60)
        self.set_setting('tools.encode.on', True)
        self.set_setting('tools.encode.encoding', 'utf-8')
        self.set_setting('tools.trailing_slash.on', True)
        self.set_setting('sponge', cdict)
        self.set_setting('sponge.root', sponge_root)
        self.set_setting('engine.autoreload_on', cdict['autoreload'])
        if 'extra' in cdict:
            self.set_setting('sponge.extra', cdict['extra'])

        application = self.validator.cdict['application']

        if 'boot' in application and \
               isinstance(application['boot'], dict):
            path = application['boot']['path']
            call = application['boot']['callable']

            cloader = ClassLoader(path)
            function = getattr(cloader.get_module(), call)

            apply(function)

        template_dir = application['template-dir']
        template_path = self.fs.join(current_full_path, template_dir)
        self.set_setting('template.dir', template_path)

        image_dir = application['image-dir']
        image_path = self.fs.join(current_full_path, image_dir)
        self.set_setting('image.dir', image_path)

        adir = application['path']
        application_path = self.fs.join(current_full_path, adir)

        cloader = ClassLoader(application_path)

        meta_conf = {}
        static = application.get('static') or {}
        for media_url, media_dir in static.items():
            media_path = self.fs.join(current_full_path, media_dir)
            meta_conf[media_url] = {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': media_path
            }

        classes = application.get('classes') or {}
        conf = meta_conf.copy()
        routed = False
        for classname, mountpoint in classes.items():
            try:
                cls = cloader.load(classname)
            except Exception, e:
                format_str = classname, application_path, unicode(e)
                sys.stderr.write('\nSponge could not find the class %s ' \
                                 'at %s, verify if your settings.yml ' \
                                 'is configured as well\n%s\n' % \
                                 (format_str))

                raise SystemExit(1)

            fallback = lambda: cherrypy.tree.mount(root=cls(),
                                                   config=conf,
                                                   script_name=mountpoint)
            msg = '\nWARNING: The class %s has no routes\n' % cls.__name__
            if not hasattr(cls, '__routes__'):
                sys.stderr.write(msg)
                fallback()
                continue

            if not isinstance(cls.__routes__, list):
                fallback()
                continue

            routed = True
            dispatcher = cherrypy.dispatch.RoutesDispatcher()
            for k, v in cls.__routes__:
                if k is None:
                    k = "%s.%s" % (cls.__name__, v['method'])

                part1 = mountpoint.rstrip('/')
                part2 = v['route'].lstrip('/')
                new_route = "/".join([part1, part2])
                dispatcher.connect(name=k,
                                   route=new_route,
                                   controller=cls(),
                                   action=v['method'])

            conf[mountpoint] = {'request.dispatch': dispatcher}

        if routed:
            cherrypy.tree.mount(root=None, config=conf)
