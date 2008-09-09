from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 4
_modified_time = 1220627655.076827
_template_filename='/home/tim/git/formish/formish/templates/mako/formish/widgets/Input.html'
_template_uri='/formish/widgets/Input.html'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding='utf-8'
from webhelpers.html import escape
_exports = []


def render_body(context,field,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(field=field,pageargs=pageargs)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'\n<input id="')
        # SOURCE LINE 2
        __M_writer(escape(field.cssname))
        __M_writer(u'" type="text" name="')
        __M_writer(escape(field.name))
        __M_writer(u'" value="')
        __M_writer(escape(field.value[0]))
        __M_writer(u'" />\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


