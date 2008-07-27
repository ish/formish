from webhelpers.html import literal
from restish.templating import render
import schemaish
from formish.dottedDict import dottedDict
from formish.converter import *
from formish.validation import *
from formish.widgets import *


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
        return self.form.data[self.name]
    
    @property
    def _data(self):
        """ Lazily get the data from the form.data when needed """
        return self.form._data[self.name]
    
    @property
    def value(self):
        """Convert the requestData to a value object for the form"""
        return self.form.requestData.get(self.name, None)
        
    @property
    def error(self):
        """ Lazily get the error from the form.errors when needed """
        return self.form.errors.get(self.name, None)
    
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

       
    
    
class Form(object):

    def __init__(self, name, structure, request, data=None, widgets=None, errors=None, requestData=None):
        self.name = name
        self.structure = Group(None, structure, self)
        self.request = request
        self._data = dottedDict(data or {})
        self.errors = dottedDict(errors or {})
        if requestData is None:
            self._requestData = None
        else:
            self._requestData = dottedDict(requestData)
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
        return convertDataToRequestData(self.structure, self._data)

    def _getRequestData(self):
        """ if we have request data then use it, if not then convert the data to request data """
        try:
            if self._requestData is None:    
                self._requestData = self.convertDataToRequestData()
            return self._requestData
        except Exception, e:
            # TODO: This is currently blowing if we can't convert the data to request data (presuming we don't already have request data)
            print '---->',e
            raise
    
    def _setRequestData(self, requestData):
        """ assign data """
        self._requestData = dottedDict(requestData)
        
    requestData = property(_getRequestData, _setRequestData)
    
    #
    # Getting the data from the form triggers a validation.
    #
    def _getData(self):
        """ validate first and raise exceptions if necessary """
        requestData = dottedDict(self.request.POST)
        errors = dottedDict()
        data = convertRequestDataToData(self.structure, requestData, errors=errors) 
        errors = validate(self.structure, data, errors=errors)
        self.errors = errors
        if len(errors.keys()) > 0:
            raise FormError('Tried to access data but conversion from request failed with %s errors (%s)'%(len(errors.keys()), errors.data))
        self._data = dottedDict(data)
        return self._data
    
    def _setData(self, data):
        """ assign data """
        ## Check that the data being set is correct for the structure on the form
        ## self.structure.attr.validate(data)
        self._data = dottedDict(data)
        
    data = property(_getData, _setData)

    
    @property
    def fields(self):
        return self.structure.fields
            
            

