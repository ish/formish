"""
Default renderer implementation for formish to use in the absence of anything
else.

The renderer is configured specifically for formish's default (they should be
considered internal, in fact) set of templates. For instance, they're UTF-8
encoded and expect to be sent to a UTF-8 HTML file, they expect substitutions
to be automatically HTML escaped, etc.

If an application completely replaces the form's renderer then it's quite
possible the application will have to reimplement all of formish's templates.
"""

from pkg_resources import resource_filename 

try:
    import mako.lookup

    class Renderer(object):

        def __init__(self, directories=None):
            if directories is None:
                directories = []
            else:
                directories = list(directories)
            directories.append(resource_filename('formish', 'templates/mako'))
            self.lookup = mako.lookup.TemplateLookup(
                    directories=directories,
                    input_encoding='utf-8', default_filters=['unicode', 'h']
                    )

        def __call__(self, template, args):
            return self.lookup.get_template(template).render_unicode(**args)

    _default_renderer = Renderer()

except ImportError, e:
    _default_renderer = None

