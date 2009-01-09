import logging
from restish import resource, templating
import formish

from pprint import pformat

from testish.lib import forms as form_defs
from testish.lib import extract_function

log = logging.getLogger(__name__)

try:
    import markdown
    def _format(v):
        v = '\n'.join([l[4:] for l in v.split('\n')])
        return markdown.markdown(v)
except ImportError:
    def _format(v):
        v = '\n'.join([l[4:] for l in v.split('\n')])
        return '<pre>%s</pre>'%v

def get_forms(ids):
    out = []
    for f in ids:
        form_def = getattr(form_defs, f)
        out.append( {'name': f,
        'title': formish.util.title_from_name(f),
        'description': _format(form_def.func_doc),
        'summary': form_def.func_doc.strip().split('\n')[0]})
    return out


class Root(resource.Resource):

    @resource.GET()
    @templating.page('root.html')
    def root(self, request):
        return {'get_forms': get_forms}
    
    def resource_child(self, request, segments):
        if segments[0] == 'filehandler':
            return formish.fileresource.FileResource(), segments[1:]
        return FormResource(segments[0]), segments[1:]


class FormResource(resource.Resource):

    def __init__(self, id):
        self.id = id
        self.title = formish.util.title_from_name(id)
        self.form_getter = getattr(form_defs,id)
        self.description = _format(self.form_getter.func_doc)
    
    @resource.GET()
    def GET(self, request):
        return self.render_form(request)

    @templating.page('form.html')
    def render_form(self, request, form=None, data=None):
        if request.GET.get('show_tests','False') == 'True':
            tests = '<h4>Selenium (Func) Tests</h4>'
            tests += extract_function.extract('functest_%s'%self.id)
            tests += '<h4>Unit Tests</h4>'
            tests += extract_function.extract('unittest_%s'%self.id)
            tests += '<a href="?show_tests=False">Click here to hide tests</a>'
        else:
            tests = '<a href="?show_tests=True">Click here to see tests</a>'
        if form is None:
            form = self.form_getter()
            form.renderer = request.environ['restish.templating.renderer']
        return {'title': self.title, 'description': self.description,
                'form': form, 'data': pformat(data),
                'template': extract_function.extract_docstring('template_%s'%self.id),
                'template_highlighted': extract_function.extract_docstring_highlighted('template_%s'%self.id),
                'definition': extract_function.extract(self.id),
                'tests': tests}
    
    @resource.POST()
    def POST(self, request):
        form = self.form_getter()
        form.renderer = request.environ['restish.templating.renderer']
        try:
            data = form.validate(request)
        except formish.FormError, e:
            return self.render_form(request, form=form)
        else:
            return self.render_form(request, form=None, data=data)
