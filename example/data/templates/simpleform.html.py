from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 4
_modified_time = 1220627655.047941
_template_filename='/home/tim/git/formish/example/example/templates/simpleform.html'
_template_uri='simpleform.html'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding='utf-8'
from webhelpers.html import escape
_exports = ['title']


def _mako_get_namespace(context, name):
    try:
        return context.namespaces[(__name__, name)]
    except KeyError:
        _mako_generate_namespaces(context)
        return context.namespaces[(__name__, name)]
def _mako_generate_namespaces(context):
    # SOURCE LINE 1
    ns = runtime.Namespace('formish', context._clean_inheritance_tokens(), templateuri='/formish/Form.html', callables=None, calling_uri=_template_uri, module=None)
    context.namespaces[(__name__, 'formish')] = ns

def _mako_inherit(template, context):
    _mako_generate_namespaces(context)
    return runtime._inherit_from(context, 'base.html', _template_uri)
def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        header = context.get('header', UNDEFINED)
        formish = _mako_get_namespace(context, 'formish')
        form = context.get('form', UNDEFINED)
        __M_writer = context.writer()
        __M_writer(u'\n')
        # SOURCE LINE 2
        __M_writer(u'\n\n<h2>')
        # SOURCE LINE 4
        __M_writer(escape(header))
        __M_writer(u'</h2>\n\n')
        # SOURCE LINE 6
        __M_writer(escape(formish.form(form)))
        __M_writer(u'\n\n')
        # SOURCE LINE 8
        __M_writer(u'\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_title(context):
    context.caller_stack._push_frame()
    try:
        header = context.get('header', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 8
        __M_writer(escape(header))
        return ''
    finally:
        context.caller_stack._pop_frame()


