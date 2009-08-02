# -*- coding: utf-8 -*-
import os
import sys
import cherrypy
from StringIO import StringIO
from mox import Mox
from nose.tools import assert_equals
from utils import assert_raises
from sponge import core
from sponge.core import SpongeConfig, ConfigValidator

config_dict = {
    'run-as': 'wsgi',
    'host': '0.0.0.0',
    'port': 80,
    'autoreload': False,
    'application': {
        'path': 'path/to/project',
        'template-dir': '/path/to/project/templates',
        'image-dir': '/path/to/project/images',
        'static': {
            '/media': 'my/media'
        },
        'classes': {
            'SomeController': '/'
        }
    }
}

def test_takes_dict_on_creation():
    cf = ConfigValidator({})
    assert_raises(TypeError, SpongeConfig, None, cf,
                  exc_pattern=r'SpongeConfig parameter 1 ' \
                  'must be a dict, got None.')
    assert_raises(TypeError, SpongeConfig, 5, cf,
                  exc_pattern=r'SpongeConfig parameter 1 ' \
                  'must be a dict, got 5.')

def test_can_set_setting():
    d = {}
    cf = ConfigValidator({})
    sp = SpongeConfig(d, cf)
    sp.set_setting('my-setting', 'my-value')
    assert_equals(d['my-setting'], 'my-value')

def test_setup_all_takes_string_path():
    d = {}
    cf = ConfigValidator({})
    sp = SpongeConfig(d, cf)
    assert_raises(TypeError, sp.setup_all, tuple(),
                  exc_pattern=r'SpongeConfig.setup_all takes a ' \
                  'string, got ().')
    assert_raises(TypeError, sp.setup_all, None,
                  exc_pattern=r'SpongeConfig.setup_all takes a ' \
                  'string, got None.')
    assert_raises(TypeError, sp.setup_all, 10,
                  exc_pattern=r'SpongeConfig.setup_all takes a ' \
                  'string, got 10.')

def test_setup_all_path_must_be_absolute():
    d = {}
    cf = ConfigValidator({})
    sp = SpongeConfig(d, cf)
    assert_raises(TypeError, sp.setup_all, 'relative/path/',
                  exc_pattern=r'SpongeConfig.setup_all takes a ' \
                  'absolute path, got relative/path/.')

def test_can_setup_all_without_routes():
    mox = Mox()
    d = {}
    class_loader = core.ClassLoader
    cherrypy = core.cherrypy
    core.ClassLoader = mox.CreateMockAnything()
    core.cherrypy = mox.CreateMockAnything()
    core.cherrypy.tree = mox.CreateMockAnything()

    cloader_mock = mox.CreateMockAnything()
    core.ClassLoader('/absolute/path/path/to/project').AndReturn(cloader_mock)

    class_mock = mox.CreateMockAnything()
    class_mock.__conf__ = {}
    cloader_mock.load('SomeController').AndReturn(class_mock)
    class_mock().AndReturn('should_be_some_controller_instance')

    core.cherrypy.tree.mount('should_be_some_controller_instance', '/', {
        '/media': {
            'tools.staticdir.dir': '/absolute/path/my/media',
            'tools.staticdir.on': True
        }
    })

    cf = core.ConfigValidator(config_dict)
    sp = core.SpongeConfig(d, cf)
    mox.ReplayAll()
    try:
        sp.setup_all('/absolute/path/')
        mox.VerifyAll()
    finally:
        core.ClassLoader = class_loader
        core.cherrypy = cherrypy

def test_setup_all_fails_on_import():
    mox = Mox()
    d = {}
    class_loader = core.ClassLoader
    cherrypy = core.cherrypy
    core.ClassLoader = mox.CreateMockAnything()
    core.cherrypy = mox.CreateMockAnything()
    core.cherrypy.tree = mox.CreateMockAnything()

    cloader_mock = mox.CreateMockAnything()
    core.ClassLoader('/absolute/path/path/to/project').AndReturn(cloader_mock)

    class_mock = mox.CreateMockAnything()
    cloader_mock.load('SomeController').AndRaise(Exception('foo error'))

    cf = core.ConfigValidator(config_dict)
    sp = core.SpongeConfig(d, cf)
    mox.ReplayAll()
    try:
        sys.stderr = StringIO()
        assert_raises(SystemExit, sp.setup_all, '/absolute/path/')
        got = sys.stderr.getvalue()
        sys.stderr = sys.__stderr__

        format_args = 'SomeController', \
                      '/absolute/path/path/to/project', \
                      'foo error'
        assert_equals(got, '\nSponge could not find the class %s ' \
                     'at %s, verify if your settings.yml ' \
                     'is configured as well\n%s\n' % format_args)
        mox.VerifyAll()
    finally:
        core.ClassLoader = class_loader
        core.cherrypy = cherrypy

def test_can_setup_all_with_routes():
    mox = Mox()
    d = {}
    class_loader = core.ClassLoader
    cherrypy = core.cherrypy
    core.ClassLoader = mox.CreateMockAnything()
    core.cherrypy = mox.CreateMockAnything()
    core.cherrypy.tree = mox.CreateMockAnything()
    core.cherrypy.dispatch = mox.CreateMockAnything()

    cloader_mock = mox.CreateMockAnything()
    core.ClassLoader('/absolute/path/path/to/project').AndReturn(cloader_mock)

    class_mock = mox.CreateMockAnything()
    class_mock.__conf__ = {
        'routes': {
            'show_photos': {
                'route': '/photos',
                'method': 'list_photos'
            },
            'edit_photo': {
                'route': '/photo/:id/edit',
                'method': 'edit'
            }
        }
    }
    controller_mock = mox.CreateMockAnything()
    cloader_mock.load('SomeController').AndReturn(class_mock)
    class_mock().AndReturn(controller_mock)
    class_mock().AndReturn(controller_mock)

    routes_mock = mox.CreateMockAnything()
    core.cherrypy.dispatch.RoutesDispatcher().AndReturn(routes_mock)

    routes_mock.connect(name='show_photos',
                        controller=controller_mock,
                        route='/photos',
                        action='list_photos')
    routes_mock.connect(name='edit_photo',
                        controller=controller_mock,
                        route='/photo/:id/edit',
                        action='edit')

    core.cherrypy.tree.mount(root=None, config={
        '/': {
            'request.dispatch': routes_mock
        },
        '/media': {
            'tools.staticdir.dir': '/absolute/path/my/media',
            'tools.staticdir.on': True
        }
    })

    cf = core.ConfigValidator(config_dict)
    sp = core.SpongeConfig(d, cf)
    mox.ReplayAll()
    try:
        sp.setup_all('/absolute/path/')
        mox.VerifyAll()
    finally:
        core.ClassLoader = class_loader
        core.cherrypy = cherrypy
