from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 4
_modified_time = 1220627260.033349
_template_filename='/home/tim/git/formish/formish/templates/mako/formish/Form.html'
_template_uri='/formish/Form.html'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding='utf-8'
from webhelpers.html import escape
_exports = ['body', 'field', 'errors', 'form', 'footer', 'actions', 'header']


def _mako_get_namespace(context, name):
    try:
        return context.namespaces[(__name__, name)]
    except KeyError:
        _mako_generate_namespaces(context)
        return context.namespaces[(__name__, name)]
def _mako_generate_namespaces(context):
    # SOURCE LINE 1
    ns = runtime.Namespace('fieldmodule', context._clean_inheritance_tokens(), templateuri='Field.html', callables=None, calling_uri=_template_uri, module=None)
    context.namespaces[(__name__, 'fieldmodule')] = ns

def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        __M_writer = context.writer()
        __M_writer(u'\n\n')
        # SOURCE LINE 9
        __M_writer(u'\n\n\n')
        # SOURCE LINE 17
        __M_writer(u'\n\n')
        # SOURCE LINE 23
        __M_writer(u'\n\n')
        # SOURCE LINE 29
        __M_writer(u'    \n    \n')
        # SOURCE LINE 41
        __M_writer(u'\n\n')
        # SOURCE LINE 46
        __M_writer(u'\n\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_body(context,form):
    context.caller_stack._push_frame()
    try:
        fieldmodule = _mako_get_namespace(context, 'fieldmodule')
        __M_writer = context.writer()
        # SOURCE LINE 25
        __M_writer(u'\n')
        # SOURCE LINE 26
        for f in form.fields:
            # SOURCE LINE 27
            __M_writer(u'      ')
            __M_writer(escape(fieldmodule.field(f)))
            __M_writer(u'\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_field(context,form):
    context.caller_stack._push_frame()
    try:
        fieldmodule = _mako_get_namespace(context, 'fieldmodule')
        __M_writer = context.writer()
        # SOURCE LINE 48
        __M_writer(u'\n ')
        # SOURCE LINE 49
        __M_writer(escape(fieldmodule.field(form)))
        __M_writer(u'\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_errors(context,form):
    context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        # SOURCE LINE 19
        __M_writer(u'\n')
        # SOURCE LINE 20
        if form.error is not None:
            # SOURCE LINE 21
            __M_writer(u'      <p class="error">')
            __M_writer(escape(form.error))
            __M_writer(u'</p>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_form(context,form):
    context.caller_stack._push_frame()
    try:
        def body(form):
            return render_body(context,form)
        def header(form):
            return render_header(context,form)
        def errors(form):
            return render_errors(context,form)
        def actions(form):
            return render_actions(context,form)
        def footer(form):
            return render_footer(context,form)
        __M_writer = context.writer()
        # SOURCE LINE 3
        __M_writer(u'\n')
        def ccall(caller):
            def body():
                __M_writer = context.writer()
                return ''
            return [body]
        caller = context.caller_stack._get_caller()
        context.caller_stack.nextcaller = runtime.Namespace('caller', context, callables=ccall(caller))
        try:
            # SOURCE LINE 4
            __M_writer(escape(header(form)))
        finally:
            context.caller_stack.nextcaller = None
        __M_writer(u'\n')
        def ccall(caller):
            def body():
                __M_writer = context.writer()
                return ''
            return [body]
        caller = context.caller_stack._get_caller()
        context.caller_stack.nextcaller = runtime.Namespace('caller', context, callables=ccall(caller))
        try:
            # SOURCE LINE 5
            __M_writer(escape(errors(form)))
        finally:
            context.caller_stack.nextcaller = None
        __M_writer(u'\n')
        def ccall(caller):
            def body():
                __M_writer = context.writer()
                return ''
            return [body]
        caller = context.caller_stack._get_caller()
        context.caller_stack.nextcaller = runtime.Namespace('caller', context, callables=ccall(caller))
        try:
            # SOURCE LINE 6
            __M_writer(escape(body(form)))
        finally:
            context.caller_stack.nextcaller = None
        __M_writer(u'\n')
        def ccall(caller):
            def body():
                __M_writer = context.writer()
                return ''
            return [body]
        caller = context.caller_stack._get_caller()
        context.caller_stack.nextcaller = runtime.Namespace('caller', context, callables=ccall(caller))
        try:
            # SOURCE LINE 7
            __M_writer(escape(actions(form)))
        finally:
            context.caller_stack.nextcaller = None
        __M_writer(u'\n')
        def ccall(caller):
            def body():
                __M_writer = context.writer()
                return ''
            return [body]
        caller = context.caller_stack._get_caller()
        context.caller_stack.nextcaller = runtime.Namespace('caller', context, callables=ccall(caller))
        try:
            # SOURCE LINE 8
            __M_writer(escape(footer(form)))
        finally:
            context.caller_stack.nextcaller = None
        __M_writer(u'\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_footer(context,form):
    context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        # SOURCE LINE 43
        __M_writer(u'\n  </div>\n</form>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_actions(context,form):
    context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        # SOURCE LINE 31
        __M_writer(u'\n    <div class="actions">\n')
        # SOURCE LINE 33
        if form.actions == []:
            # SOURCE LINE 34
            __M_writer(u'        <input type="submit" id="')
            __M_writer(escape(form.name))
            __M_writer(u'-action-submit" name="submit" value="Submit" />\n')
            # SOURCE LINE 35
        else:
            # SOURCE LINE 36
            for action in form.actions:
                # SOURCE LINE 37
                __M_writer(u'        <input type="submit" id="')
                __M_writer(escape(form.name))
                __M_writer(u'-action-')
                __M_writer(escape(action.name))
                __M_writer(u'" name="')
                __M_writer(escape(action.name))
                __M_writer(u'" value="')
                __M_writer(escape(action.label))
                __M_writer(u'" />\n')
        # SOURCE LINE 40
        __M_writer(u'    </div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_header(context,form):
    context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        # SOURCE LINE 12
        __M_writer(u'\n<form id="')
        # SOURCE LINE 13
        __M_writer(escape(form.name))
        __M_writer(u'" action="')
        __M_writer(escape(form._action))
        __M_writer(u'" class="formish-form" method="post" enctype="multipart/form-data" accept-charset="utf-8">\n  <div>\n    <input type="hidden" name="_charset_" />\n    <input type="hidden" name="__formish_form__" value="')
        # SOURCE LINE 16
        __M_writer(escape(form.name))
        __M_writer(u'" />\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


