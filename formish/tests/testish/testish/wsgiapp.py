from restish.app import RestishApp
from restish.templating import Templating

from testish.resource import root

import os, pkg_resources
from restish.contrib.makorenderer import MakoRenderer
import mimetypes
try: 
    mimetypes.init() 
except AttributeError: 
    pass 

def make_app(global_conf, **app_conf):
    """
    PasteDeploy WSGI application factory.

    Called by PasteDeply (or a compatable WSGI application host) to create the
    testish WSGI application.
    """
    app = RestishApp(root.Root())
    app = setup_environ(app, global_conf, app_conf)
    return app


def setup_environ(app, global_conf, app_conf):
    """
    WSGI application wrapper factory for extending the WSGI environ with
    application-specific keys.
    """

    # Create any objects that should exist for the lifetime of the application
    # here. Don't forget to actually include them in the environ though! For
    # example:
    renderer = MakoRenderer(
        directories=[pkg_resources.resource_filename('testish', 'templates'),
        pkg_resources.resource_filename('formish', 'templates/mako')],
        module_directory=os.path.join(app_conf['cache_dir'], 'templates'),
        input_encoding='utf-8', output_encoding='utf-8',
        default_filters=['unicode', 'h'])

    def application(environ, start_response):

        # Add additional keys to the environ here. For example:
        #
        environ['restish.templating'] = Templating(renderer)

        return app(environ, start_response)

    return application

