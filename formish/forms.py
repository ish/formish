from webhelpers.html import literal
from restish.templating import render
import schemaish
from formish.converter import string_converter
from formish import validation


# Singleton used to represent no argument passed, for when None is a valid
# value for the arg.
NOARG = object()


def validate(structure, requestData, errors=None, data=None):
    """ Take a schemaish structure and use it's validators to return any errors"""
    errors = errors or {}
    data = data or {}
    # Use formencode to validate each field in the schema, return 
    # a dictionary of errors keyed by field name
    for attr in structure.attrs:
        try:
            if hasattr(attr[1],'attrs'):
                d, e = validate(attr[1], requestData[attr[0]], errors=errors.get(attr[0],{}), data=data.get(attr[0],{}))
                if len(e.keys()) != 0:
                    errors[attr[0]] = e
                else:
                    data[attr[0]] = d
            else: 
                attr[1].validate(requestData.get(attr[0]))
        except schemaish.Invalid, e:
            errors[attr[0]] = e
    return data, errors

def convertDataToRequestData(formStructure, data, requestData=None, errors=None):
    """ Take a form structure and use it's widgets to convert data to request data """
    if requestData is None:
        requestData = {}
    if errors is None:
        errors = {}
    for field in formStructure.fields:
        try:
            if hasattr(field[1],'fields'):
                c, e = convertDataToRequestData(field, data[field.attr.name], requestData=requestData.get(field.attr.name,{}), errors=errors.get(field.attr.name, {}))
                if len(e.keys()) != 0:
                    errors[field.attr.name] = e
            else: 
                field.widget.pre_render(field.attr,data.get(field.attr.name))
        except schemaish.Invalid, e:
            errors[attr[0]] = e
    return errors

def setDict(out, keys, value):
    if len(keys) == 1:
        if out.has_key(keys[0]):
            raise KeyError('Clash in keys when converting from dotted to nested')
        out[keys[0]] = value
    else:
        if not out.has_key(keys[0]):
            out[keys[0]] = {}
        return setDict(out[keys[0]], keys[1:], value)


def getDictFromDottedDict(data):
    out = {}
    keyslist=[key.split('.') for key in data.keys()]
    keyslist.sort(reverse=True)
    for keys in keyslist:
        setDict(out, keys, data['.'.join(keys)])
    return out    


def getDataUsingDottedKey(data, dottedkey, default=NOARG):
    keys = dottedkey.split('.')
    d = data
    try:
        for key in keys:
            d = d[key]
    except KeyError, e:
        if default is not NOARG:
            return default
        raise KeyError('Dotted key does not exist')
    return d
        

class Field(object):
    """
    A wrapper for a schema field type that includes form information. 
    
    The Schema field does not have any bindings to the form libaray, it can be used on it's own. The Bound field.
    
    The _widget attribute is a base widget to which the real widget is bound 
    
    """

    def __init__(self, name, attr, form):
        """
        @param name:            Fields dotted name
        @type name:             String
        @param attr_name:       a name for the field
        @type attr_name:        String
        @param attr:            a Schema attr to bind to the container
        @type attr:             Attribute object
        """
        self.name = name
        self.attr = attr
        self._widget = Widget()
        self.form = form

    @property
    def title(self):
        return self.attr.title

    @property
    def description(self):
        return self.attr.description        
        
    def __call__(self):
        """Default template renderer for the field (not the widget itself) """
        return literal(render(self.form.request, "formish/field.html", {'field': self}))
    
    @property
    def data(self):
        """ Lazily get the data from the form.data when needed """
        return getDataUsingDottedKey(self.form.data, self.name)
    
    @property
    def _data(self):
        """ Lazily get the data from the form.data when needed """
        return getDataUsingDottedKey(self.form._data, self.name)    
    
    @property
    def value(self):
        """Convert the form.data to a value object for the form"""
        return getDataUsingDottedKey(self.form.requestData, self.name, None)
        
    @property
    def error(self):
        """ Lazily get the error from the form.errors when needed """
        return getDataUsingDottedKey(self.form.errors, self.name, None)
    
    def _getWidget(self):
        return BoundWidget(self._widget, self)
    
    def _setWidget(self, widget):
        self._widget = widget
        
    widget = property(_getWidget, _setWidget)
    

class Group(object):

    def __init__(self, name, attr, form):
        """
        @param name:            Fields dotted name
        @type name:             String
        @param attr_name:       a name for the field
        @type attr_name:        String
        @param attr:            a Schema attr to bind to the container
        @type attr:             Attribute object
        """
        self.name = name
        self.attr = attr
        self._widget = Widget()
        self.form = form
        self._fields = {}    

    @property
    def title(self):
        return self.attr.title

    @property
    def description(self):
        return self.attr.description        
        
    @property
    def attrs(self):
        return self.attr.attrs
    
    @property
    def fields(self):
        for attr in self.attr.attrs:
            yield self.bind(attr[0], attr[1])        
    
    def __getattr__(self, name):
        return self.bind( name, self.attr.get(name) )

    def bind(self, attr_name, attr):
        try:
            return self._fields[attr_name]
        except KeyError:
            if self.name is None:
                keyprefix = attr_name
            else:
                keyprefix = '%s.%s'%(self.name,attr_name)
            if isinstance( attr, schemaish.Structure ):
                bf = Group(keyprefix, attr, self.form)
            else:
                bf = Field(keyprefix, attr, self.form)
            self._fields[attr_name] = bf
            return bf
        
    def __call__(self):
        return literal(render(self.form.request, "formish/structure.html", {'field': self, 'fields': self.fields}))

        
class BoundWidget(object):
    
    def __init__(self, widget, field):
        self.widget = widget
        self.field = field
        
    def __call__(self):
        return self.widget(self.field)


class Widget(object):
    
    converter = string_converter
    
    def pre_render(self, schemaType, data):
        if self.converter is None:
            return data
        return self.converter(schemaType).fromType(data)

    def validate(self, data):
        errors = None
        return data, errors

    def __call__(self, field):
        return literal(render(field.form.request, "formish/widgets/default.html", {'widget': self, 'field': field}))

class Input(Widget):
    
    converter = string_converter

    def pre_render(self, schemaType, data):
        if self.converter is None:
            return data
        return self.converter(schemaType).fromType(data)

    def validate(self, data):
        errors = None
        return data, errors
    
    def __call__(self, field):
        return literal(render(field.form.request, "formish/widgets/input.html", {'widget': self, 'field': field}))
    
    

    
    
    
class TextArea(Widget):
    
    def __init__(self, cols=None, rows=None):
        if cols is not None:
            self.cols = cols
        if rows is not None:
            self.rows = rows 
            
    def __call__(self, form, field):
        return literal(render(form.request, "formish/widgets/textarea.html", {'widget': self, 'field': field}))
    
    
class Form(object):

    def __init__(self, name, structure, request, data=None, widgets=None, errors=None, requestData=None):
        self.name = name
        self.structure = Group(None, structure, self)
        self.request = request
        self.data = data or {}
        self.errors = errors or {}
        self._requestData = requestData or {}
        self.set_widgets(self.structure, widgets)
        
    def set_widgets(self, structure, widgets):
        if not widgets: 
            return
        for name, widget in widgets.iteritems():
            form_item = getattr(structure, name)
            if isinstance(widget, dict):
                # We have a dict of widgets presumably desitined for form_item that *should* be a bound structure.
                self.set_widgets( form_item, widget )
            else:
                # Set the widget on this form item
                form_item.widget = widget

    def __call__(self):
        return literal(render(self.request, "formish/form.html", {'form': self}))

    def __getattr__(self, name):
        return getattr( self.structure, name )

    
    #
    # Getting the requestData from the form converts self.data if necessary.
    #        
    def convertDataToRequestData(self):
        return convertDataToRequestData(self.structure, self.data)

    def _getRequestData(self):
        """ if we have request data then use it, if not then convert the data to request data """
        if self.requestData is None:
            self._requestData = self.convertDataToRequestData()
        return self._requestData
    
    def _setRequestData(self, requestData):
        """ assign data """
        self._requestData = requestData
        
    requestData = property(_getRequestData, _setRequestData)
    
    #
    # Getting the data from the form triggers a validation.
    #
    def _getData(self):
        """ validate first and raise exceptions if necessary """
        data = getDictFromDottedDict(self.request.POST)
        data, errors = validate(self.structure, data)
        self._data = data
        self.errors = errors
        if len(errors) > 0:
            raise validation.FormError('Tried to access data but conversion from request failed with %s errors (%s)'%(len(errors), errors))
        return self._data
    
    def _setData(self, data):
        """ assign data """
        self._data = data
        
    data = property(_getData, _setData)

    
    @property
    def fields(self):
        return self.structure.fields
            
    def validateRequest(self):
        """
        Takes the request data and runs the validators against it.
        """
        data, errors = validate(self.structure, self.request.POST)
        self.data = data
        self.errors = errors

        return len(errors.keys()) == 0
            

