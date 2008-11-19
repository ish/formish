"""Pylons middleware initialization"""
import os
import pkg_resources
from beaker.middleware import CacheMiddleware, SessionMiddleware
from paste.cascade import Cascade
from paste.registry import RegistryManager
from paste.urlparser import StaticURLParser
from paste.deploy.converters import asbool
from pylons import config
from pylons.middleware import ErrorHandler, StaticJavascripts, \
    StatusCodeRedirect
from restish.app import RestishApp
from restish.contrib.makorenderer import MakoRenderer

from example.config.environment import load_environment
from example.resources.root import RootResource

def environ_setup_app(app, environ_extras):
    def f(environ, start_response):
        environ.update(environ_extras)
        return app(environ, start_response)
    return f

def make_app(global_conf, full_stack=True, **app_conf):
    """Create a Pylons WSGI application and return it

    ``global_conf``
        The inherited configuration for this application. Normally from
        the [DEFAULT] section of the Paste ini file.

    ``full_stack``
        Whether or not this application provides a full WSGI stack (by
        default, meaning it handles its own exceptions and errors).
        Disable full_stack when this application is "managed" by
        another WSGI middleware.

    ``app_conf``
        The application's local configuration. Normally specified in the
        [app:<name>] section of the Paste ini file (where <name>
        defaults to main).
    """
    # Configure the Pylons environment
    load_environment(global_conf, app_conf)

    # The Pylons WSGI app
    app = RestishApp(RootResource())
    
    renderer = MakoRenderer(
            directories=[
                pkg_resources.resource_filename('example', 'templates'),
                pkg_resources.resource_filename('formish', 'templates/mako')],
            module_directory=os.path.join(app_conf['cache_dir'], 'templates'),
            input_encoding='utf-8', output_encoding='utf-8',
            default_filters=['unicode', 'h'])

    # Add infomy keys to the environ.
    app = environ_setup_app(app, {'restish.templating.renderer': renderer})
    
    # CUSTOM MIDDLEWARE HERE (filtered by error handling middlewares)
    
    # Routing/Session/Cache Middleware
    app = SessionMiddleware(app, config)
    app = CacheMiddleware(app, config)
    
    if asbool(full_stack):
        # Handle Python exceptions
        app = ErrorHandler(app, global_conf, **config['pylons.errorware'])

        # Display error documents for 401, 403, 404 status codes (and
        # 500 when debug is disabled)
        if asbool(config['debug']):
            app = StatusCodeRedirect(app)
        else:
            app = StatusCodeRedirect(app, [400, 401, 403, 404, 500])

    # Establish the Registry for this application
    app = RegistryManager(app)

    # Static files (If running in production, and Apache or another web 
    # server is handling this static content, remove the following 3 lines)
    javascripts_app = StaticJavascripts()
    static_app = StaticURLParser(config['pylons.paths']['static_files'])
    app = Cascade([static_app, javascripts_app, app])
    return app
