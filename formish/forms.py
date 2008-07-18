from webhelpers.html import literal
from pylons.templating import render

import formencode

def keytoid(name, key):
    # Create a combined key from the form name and the field name (key)
    return '%s-%s'%(name,key)

def validate(schema, data, name):
    # Use formencode to validate each field in the schema, return 
    # a dictionary of errors keyed by field name
    errors = {}
    for field in schema.fields:
        try:
            if field.validator is not None:
                field.validator.to_python(data.get(field.name,None))
        except formencode.Invalid, e:
            errors[field.name] = e
    return errors


class Schema(object):
    """
    Simple object to hold field definitions
    """

    def __init__(self):
        self.fields = []

    def add(self, field):
        self.fields.append(field)

    def get(self, name):
        for field in self.fields:
            if field.name == name:
                return field
        raise KeyError(name)


class Field(object):
    """
    A field definion for the Schema object
    
    Keyword arguments:
    
    @param name:          a text id 
    @type name:           camelcase string [a-zA-Z]
    @param title:         a short title for the field (used as a label on forms)
    @type title:          string - short sentence
    @param description:   longer description of this field 
    @type description:    string - a paragraph at most
    @param readonly:      a flag to mark the field as readonly
    @type readonly:       boolean
    @param default:       default value for the field
    @type default:        any
    @param validator:     a formencode validator
    @type validator:      formencode.validator object

    """

    def __init__(self, name, title, description=None, readonly=None, default=None, validator=None):
        self.name = name
        self.title = title
        self.description = description
        self.readonly = readonly
        self.default = default
        self.validator = validator


class String(Field):
    """
    Marker object for String schema type
    """
    pass


class BoundField(object):
    """
    A wrapper for a schema field type that includes form information. 
    
    The Schema field does not have any bindings to the form libaray, it can be used on it's own. The Bound field.
    
    The _widget attribute is a base widget to which the real widget is bound 
    
    """

    def __init__(self, form, field):
        """
        @param form:       a form to bind the field to
        @type form:        Form object
        @param field:      a Schema field to bind with the form
        @type field:       Field object
        """
        
        self.form = form
        self.field = field
        self._widget = Widget()

    def __call__(self):
        """Default template renderer for the field (not the widget itself) """
        return literal(render("forms/field.html", field=self, form=self.form))
    
    @property
    def value(self):
        """ Lazily get the value from the form.data when needed """
        return self.form.data.get(self.field.name)

    @property
    def error(self):
        """ Lazily get the error from the form.errors when needed """
        return self.form.errors.get(self.field.name)
    
    @property
    def originalname(self):
        """ The original, un-bound, field name """
        return self.field.name

    @property
    def name(self):
        return keytoid(self.form.name, self.field.name)
    
    @property
    def title(self):
        return self.field.title

    @property
    def description(self):
        return self.field.description
    
    def _getWidget(self):
        return BoundWidget(self._widget, self.form, self)
    
    def _setWidget(self, widget):
        self._widget = widget
        
    widget = property(_getWidget, _setWidget)
    
    
class BoundWidget(object):
    
    def __init__(self, widget, form, field):
        self.widget = widget
        self.form = form
        self.field = field
        
    def __call__(self):
        return self.widget(self.form, self.field)


class Widget(object):

    def __call__(self, form, field):
        return literal(render("forms/widgets/default.html", widget=self, form=form, field=field))


class Form(object):

    def __init__(self, name, schema, data={}, widgets={}, errors={}):
        self.name = name
        self.schema = schema
        self.boundfields = {}
        self.data = data
        self.errors = errors
        for name, widget in widgets.iteritems():
            bf = self.bind(self.schema.get(name))
            bf.widget=widget


    def __call__(self):
        return literal(render("forms/form.html", form=self))

    def __getattr__(self, name):
        return self.bind(self.schema.get(name))

    def bind(self, field):
        try:
            return self.boundfields[field.name]
        except KeyError:
            bf = BoundField(self, field)
            self.boundfields[field.name] = bf
            return bf

    @property
    def fields(self):
        for field in self.schema.fields:
            yield self.bind(field)
            
    def validateRequest(self,request):
        data = {}
        for f in self.fields:
            data[ f.originalname ] = request.POST.get( keytoid(self.name, f.originalname), None ) 
        errors = validate(self.schema, data, self.name)
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
        return literal(render("forms/widgets/textarea.html", widget=self, form=form, field=field))
            
            
            
class TextArea_(Widget):
    
    def __init__(self, cols=None, rows=None):
        if cols is not None:
            self.cols = cols
        if rows is not None:
            self.rows = rows 
            
    def __call__(self):
        return literal(render("forms/widgets/textarea.html", widget=self, form=self.form, field=self.field))
            
            