import logging
import os.path
from datetime import datetime
import tempfile
import uuid
from restish import resource, templating, http
import formish
from formish import fileresource, filestore

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
        form_attr = 'form_%s'%f
        form_def = getattr(form_defs, form_attr)
        out.append( {'name': f,
        'title': formish.util.title_from_name(f),
        'description': _format(form_def.func_doc),
        'summary': form_def.func_doc.strip().split('\n')[0]})
    return out



class FileAccessor(object):

    def __init__(self):
        self.prefix = 'store-%s'%tempfile.gettempprefix()
        self.tempdir = tempfile.gettempdir()
        self.mtime_cache = True

    def _abs(self, filename):
        return '%s/%s%s'% (self.tempdir, self.prefix, filename.split('-')[-1])

    def get_file(self, filename):
        return open(self._abs(filename)).read()

    def file_exists(self, filename):
        return os.path.exists(self._abs(filename))

    def cacheattr(self, filename):
        try:
            mtime = datetime.fromtimestamp( os.path.getmtime(self._abs(filename)) )
        except OSError:
            raise KeyError
        return mtime


class Root(resource.Resource):

    @resource.GET()
    @templating.page('root.html')
    def root(self, request):
        return {'get_forms': get_forms}

    def resource_child(self, request, segments):
        if segments[0] == 'filehandler':
            return fileresource.FileResource.quickstart('store', 'cache'), segments[1:]
        return FormResource(segments[0]), segments[1:]


class FormResource(resource.Resource):

    def __init__(self, id):
        self.id = id
        self.title = formish.util.title_from_name(id)
        self.form_attr = 'form_%s'%id
        try:
            self.form_getter = getattr(form_defs,self.form_attr)
        except AttributeError:
            raise http.NotFoundError()
        self.description = _format(self.form_getter.func_doc)
        self.filestore = filestore.CachedTempFilestore(filestore.FileSystemHeaderedFilestore('store'))

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
            form = self.form_getter(request)
            form.renderer = request.environ['restish.templating'].renderer
        return {'title': self.title, 'description': self.description,
                'form': form, 'data': pformat(data),'rawdata': data,
                'template': extract_function.extract_docstring('template_%s'%self.id),
                'template_highlighted': extract_function.extract_docstring_highlighted('template_%s'%self.id),
                'definition': extract_function.extract(self.form_attr).replace('6LcSqgQAAAAAAGn0bfmasP0pGhKgF7ugn72Hi2va','6LcSqgQA......................ugn72Hi2va'),
                'tests': tests}

    @resource.POST()
    def POST(self, request):
        form = self.form_getter(request)
        form.renderer = request.environ['restish.templating'].renderer
        try:
            data = form.validate(request)
        except formish.FormError:
            return self.render_form(request, form=form)
        else:
            if 'myFileField' in data and data['myFileField'] is not None:
                f = data['myFileField']
                self.filestore.put(f.filename, f.file, uuid.uuid4().hex, [('Content-Type', f.mimetype)])

            return self.render_form(request, form=None, data=data)
