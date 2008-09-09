from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 4
_modified_time = 1220630013.0516429
_template_filename='/home/tim/git/formish/example/example/templates/root.html'
_template_uri='root.html'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding='utf-8'
from webhelpers.html import escape
_exports = []


def _mako_get_namespace(context, name):
    try:
        return context.namespaces[(__name__, name)]
    except KeyError:
        _mako_generate_namespaces(context)
        return context.namespaces[(__name__, name)]
def _mako_generate_namespaces(context):
    pass
def _mako_inherit(template, context):
    _mako_generate_namespaces(context)
    return runtime._inherit_from(context, 'base.html', _template_uri)
def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        forms = context.get('forms', UNDEFINED)
        menu = context.get('menu', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'\n\n<p>Formish Examples</p>\n\n<p>Some interactive form examples:</p>\n\n<ul>\n')
        # SOURCE LINE 8
        for m in menu:
            # SOURCE LINE 9
            __M_writer(u'  <li><a href="/')
            __M_writer(escape(m))
            __M_writer(u'">')
            __M_writer(escape(forms[m][0]))
            __M_writer(u'</a> -- ')
            __M_writer(escape(forms[m][1]))
            __M_writer(u'</li>\n')
        # SOURCE LINE 11
        __M_writer(u'</ul>\n\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


