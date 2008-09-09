from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 4
_modified_time = 1220629200.240572
_template_filename='/home/tim/git/formish/example/example/templates/base.html'
_template_uri='base.html'
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
    ns = runtime.Namespace('formish', context._clean_inheritance_tokens(), templateuri='formish/Form.html', callables=None, calling_uri=_template_uri, module=None)
    context.namespaces[(__name__, 'formish')] = ns

def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        self = context.get('self', UNDEFINED)
        __M_writer = context.writer()
        __M_writer(u'\n<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">\n\n<head>\n  <meta content="text/html; charset=UTF-8" http-equiv="content-type" />\n  <meta name="description" value="" />\n  <meta name="keywords" value="" />\n  <title>')
        # SOURCE LINE 8
        __M_writer(escape(self.title()))
        __M_writer(u'</title>\n  <link href="/css/forms.css" type="text/css" rel="stylesheet" />\n</head>\n\n<body class="">\n<div id="header">\n  <h1>Formish</h1>\n</div>\n<div id="body">\n  ')
        # SOURCE LINE 17
        __M_writer(escape(self.body()))
        __M_writer(u'\n</div>\n\n\n<div id="footer">\n  &copy; <strong class="infomy">Tim and Matt</strong> \n</div>\n\n</body>\n</html>\n\n')
        # SOURCE LINE 34
        __M_writer(u'\n\n\n\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_title(context):
    context.caller_stack._push_frame()
    try:
        self = context.get('self', UNDEFINED)
        hasattr = context.get('hasattr', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 28
        __M_writer(u'\n')
        # SOURCE LINE 29
        if hasattr(self, 'page_title'):
            # SOURCE LINE 30
            __M_writer(u'  ')
            __M_writer(escape(self.page_title()))
            __M_writer(u' @ infomy\n')
            # SOURCE LINE 31
        else:
            # SOURCE LINE 32
            __M_writer(u'  infomy\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


