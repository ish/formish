from webhelpers.html import literal
from restish.templating import render

import formencode

import wingdbstub

def keytoid(name, key):
    # Create a combined key from the form name and the attr name (key)
    return '%s-%s'%(name,key)


def validate(schema, data, name):
    # Use formencode to validate each field in the schema, return 
    # a dictionary of errors keyed by field name
    errors = {}
    for attr in schema.attrs:
        try:
            if attr[1].validator is not None:
                attr[1].validator.to_python(data.get(attr[0],None))
        except formencode.Invalid, e:
            errors[attr[0]] = e
    return errors


class Field(object):
    """
    A wrapper for a schema field type that includes form information. 
    
    The Schema field does not have any bindings to the form libaray, it can be used on it's own. The Bound field.
    
    The _widget attribute is a base widget to which the real widget is bound 
    
    """

    def __init__(self, container, attr, form):
        """
        @param container:       a structure object to bind the field to
        @type container:        Structure object 
        @param attr:      a Schema attr to bind to the container
        @type attr:       Attribute object
        """
        
        self.container = container
        self.attr = attr
        self._widget = Widget()
        self.form = form
        self._fields = {}

    def __call__(self):
        """Default template renderer for the field (not the widget itself) """
        if hasattr(self.attr[1],'attrs'):
            return literal(render(self.form.request, "formish/structure.html", {'field': self, 'fields': self.fields}))
        else:
            return literal(render(self.form.request, "formish/field.html", {'field': self}))
    
    @property
    def value(self):
        """ Lazily get the value from the form.data when needed """
        return self.container.values.get(self.name)

    @property
    def values(self):
        return self.container.values.get(self.name, {})
        
    @property
    def error(self):
        """ Lazily get the error from the form.errors when needed """
        return self.errors.get(self.name)

    @property
    def errors(self):
        return self.container.errors
    
    @property
    def originalname(self):
        """ The original, un-bound, field name """
        return self.attr[0]

    @property
    def name(self):
        return keytoid(self.container.name, self.originalname)
    
    @property
    def title(self):
        return self.attr[1].title

    @property
    def fields(self):
        for attr in self.attr[1].attrs:
            yield self.bind(attr)
            
    
    @property
    def description(self):
        return self.attr[1].description

    
    def __getattr__(self, name):
        return self.bind(self.attr[1].get(name))

    def bind(self, attr):
        try:
            return self._fields[attr[0]]
        except KeyError:
            bf = Field(self, attr, self.form)
            if hasattr(attr[1],'attrs'):
                for a in attr[1].attrs:
                    bf.bind(a)
            self._fields[attr[0]] = bf
            return bf
    
    
    def _getWidget(self):
        return BoundWidget(self._widget, self)
    
    def _setWidget(self, widget):
        self._widget = widget
        
    
        
    widget = property(_getWidget, _setWidget)
    
    
class BoundWidget(object):
    
    def __init__(self, widget, field):
        self.widget = widget
        self.field = field
        
    def __call__(self):
        return self.widget(self.field)


class Widget(object):

    def __call__(self, field):
        return literal(render(field.form.request, "formish/widgets/default.html", {'widget': self, 'field': field}))


class Form(object):

    def __init__(self, name, structure, request, data={}, widgets={}, errors={}):
        self.name = name
        self.structure = structure
        self.request = request
        self._fields = {}
        self.data = data
        self.errors = errors
        for name, widget in widgets.iteritems():
            bf = self.bind(self.structure.get(name))
            bf.widget=widget


    def __call__(self):
        return literal(render(self.request, "formish/form.html", {'form': self}))

    def __getattr__(self, name):
        return self.bind(self.structure.get(name))

    def bind(self, attr):
        try:
            return self._fields[attr[0]]
        except KeyError:
            bf = Field(self, attr, self)
            if hasattr(attr[1],'attrs'):
                for a in attr[1].attrs:
                    bf.bind(a)
            self._fields[attr[0]] = bf
            return bf

    @property
    def values(self):
        return {}
    
    @property
    def fields(self):
        for attr in self.structure.attrs:
            yield self.bind(attr)
            
    def validateRequest(self):
        data, errors = validate(self.schema, request.POST, context='POST')
        self.data = data
        self.errors = errors
        return len(errors.keys()) == 0
            

class TextArea(object):
    
    def __init__(self, cols=None, rows=None):
        if cols is not None:
            self.cols = cols
        if rows is not None:
            self.rows = rows 
            
    def __call__(self, form, field):
        return literal(render(form.request, "formish/widgets/textarea.html", {'widget': self, 'field': field}))
