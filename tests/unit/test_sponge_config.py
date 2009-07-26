# -*- coding: utf-8 -*-
import os
import cherrypy
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

def test_can_setup_all():
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
