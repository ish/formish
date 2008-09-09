from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 4
_modified_time = 1220950031.230186
_template_filename='/home/tim/git/formish/formish/templates/mako/formish/Field.html'
_template_uri='/formish/Field.html'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding='utf-8'
from webhelpers.html import escape
_exports = ['field', 'widget']


def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        __M_writer = context.writer()
        # SOURCE LINE 32
        __M_writer(u'\n\n')
        # SOURCE LINE 36
        __M_writer(u'\n\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_field(context,f):
    context.caller_stack._push_frame()
    try:
        def field(f):
            return render_field(context,f)
        def widget(field):
            return render_widget(context,field)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'\n')
        # SOURCE LINE 2
        if 'Field' in f.__class__.__name__:
            # SOURCE LINE 3
            __M_writer(u'<div id="')
            __M_writer(escape(f.cssname))
            __M_writer(u'-field" class="')
            __M_writer(escape(f.classes))
            __M_writer(u'">\n')
            # SOURCE LINE 4
            if f.widget.widget.__class__.__name__ != 'Hidden':
                # SOURCE LINE 5
                __M_writer(u'  <label for="')
                __M_writer(escape(f.cssname))
                __M_writer(u'">')
                __M_writer(escape(f.title))
                __M_writer(u'</label>\n')
            # SOURCE LINE 7
            __M_writer(u'  <div class="inputs">\n    ')
            # SOURCE LINE 8
            __M_writer(escape(widget(f)))
            __M_writer(u'\n  </div>\n')
            # SOURCE LINE 10
            if f.widget.widget.__class__.__name__ != 'Hidden':
                # SOURCE LINE 11
                if f.error:
                    # SOURCE LINE 12
                    __M_writer(u'  <span class="error">')
                    __M_writer(escape(f.error))
                    __M_writer(u'</span>\n')
                # SOURCE LINE 14
                if f.description:
                    # SOURCE LINE 15
                    __M_writer(u'  <span class="description">')
                    __M_writer(escape(f.description))
                    __M_writer(u'</span>\n')
            # SOURCE LINE 18
            __M_writer(u'</div>\n')
            # SOURCE LINE 19
        else:
            # SOURCE LINE 20
            __M_writer(u'<fieldset class="group" id="')
            __M_writer(escape(f.cssname))
            __M_writer(u'-field" class="')
            __M_writer(escape(f.classes))
            __M_writer(u'">\n')
            # SOURCE LINE 21
            if f.title:
                # SOURCE LINE 22
                __M_writer(u'  <legend>')
                __M_writer(escape(f.title))
                __M_writer(u'</legend>\n')
            # SOURCE LINE 24
            if f.description:
                # SOURCE LINE 25
                __M_writer(u'  <div class="description">')
                __M_writer(escape(f.description))
                __M_writer(u'</div>\n')
            # SOURCE LINE 27
            for ff in f.fields:
                # SOURCE LINE 28
                __M_writer(u'      ')
                __M_writer(escape(field(ff)))
                __M_writer(u'\n')
            # SOURCE LINE 30
            __M_writer(u'</fieldset>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_widget(context,field):
    context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        # SOURCE LINE 34
        __M_writer(u'\n')
        # SOURCE LINE 35
        runtime._include_file(context, 'widgets/' + field.widget.widget.__class__.__name__ + '.html', _template_uri, field=field)
        __M_writer(u'\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


