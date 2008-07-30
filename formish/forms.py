from webhelpers.html import literal
from restish.templating import render
import schemaish
from formish import util
from formish.dottedDict import dottedDict
from formish.converter import *
from formish.validation import *
from formish.widgets import *
from formish import util


class Action(object):
    """Tracks an action that has been added to a form.
    """
    def __init__(self, callback, name, label):

        if not util.valid_identifier(name):
            raise FormError('Invalid action name %r.'%name)

        self.callback = callback
        self.name = name
        if label is None:
            self.label = util.titleFromName(name)
        else:
            self.label = label

class Field(object):
    """
    A wrapper for a schema field type that includes form information. 
    
    The Schema field does not have any bindings to the form library, it can be
    used on it's own. The Bound field.
    
    The _widget attribute is a base widget to which the real widget is bound 
    """

    def __init__(self, name, attr, form):
        """
        @param name:            Fields dotted name
        @type name:             String
        @param attr:            a Schema attr to bind to the container
        @type attr:             Attribute object
        @param form:            The form the field belongs to.
        @type form:             Form instance.
        """
        self.name = name
        self.attr = attr
        self.form = form
        # Create a default widget for the field. XXX There is no such thing as
        # a default widget, this needs to be some sort of adaption process.
        self._widget = Widget()
        # Construct a title
        self.title = self.attr.title
        if self.title is None:
            self.title = util.title_from_name(self.name.split('.')[-1])

    @property
    def cssname(self):
        return '%s-%s'%(self.form.name, '-'.join(self.name.split('.')))
    
    @property
    def classes(self):
        classes = [
            'field',
            self.attr.__class__.__name__.lower(),
            self.widget.widget.__class__.__name__.lower(),
            ]
        if self.required:
            classes.append('required')
        if self.widget.cssClass:
            classes.append(self.widget.cssClass)        
        if self.error:
            classes.append('error')
        return ' '.join(classes)
   
    @property 
    def required(self):
        hasrequiredvalidator = self.isNotEmpty(self.attr.validator)
        return hasrequiredvalidator
    
    def isNotEmpty(self,validator):
        if validator is None:
            return False
        if isinstance(validator, schemaish.NotEmpty) or getattr(validator,'not_empty'):
            return True
        if hasattr(validator,'validators'):
            for v in validator.validators:
                self.isNotEmpty(v)
        return False
        
        
    
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
        return self.form.requestData.get(self.name, [None])
        
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
        self.form = form
        self._fields = {}    
        # Create a default widget for the group. XXX Shouldn't this be some
        # sort of GroupWidget?
        self._widget = Widget()
        # Construct a title
        self.title = self.attr.title
        if self.title is None and name is not None:
            self.title = util.title_from_name(self.name.split('.')[-1])

    @property
    def cssname(self):
        return '%s-%s'%(self.form.name, '-'.join(self.name.split('.')))
    
    @property
    def classes(self):
        classes = [
            'field',
            self.attr.__class__.__name__.lower(),
            self.widget.widget.__class__.__name__.lower(),
            ]
        if self.required:
            classes.append('required')
        if self.widget.cssClass:
            classes.append(self.widget.cssClass)        
        if self.error:
            classes.append('error')
        return ' '.join(classes)            
            
    @property 
    def required(self):
        validator = self.attr.validator
        if validator is not None:
            for v in validator:
                if isinstance(v,schemaish.NotEmpty):
                    return true
        return False
        
        
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

    @property
    def error(self):
        """ Lazily get the error from the form.errors when needed """
        return self.form.errors.get(self.name, None)        
        
    def __call__(self):
        return literal(render(self.form.request, "formish/structure.html", {'group': self, 'fields': self.fields}))

    def _getWidget(self):
        return BoundWidget(self._widget, self)
    
    def _setWidget(self, widget):
        self._widget = widget
        
    widget = property(_getWidget, _setWidget)   
    
    
class Form(object):

    def __init__(self, name, structure, request, data=None, widgets=None, errors=None, requestData=None):
        self.name = name
        self.structure = Group(None, structure, self)
        self.request = request
        self._data = dottedDict(data or {})
        self.errors = dottedDict(errors or {})
        self.actions = []
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

    def addAction(self, callback, name="submit", label=None):
        if name in [action.name for action in self.actions]:
            raise ValueError('Action with name %r already exists.' % name)
        self.actions.append( Action(callback, name, label) )              

    def action(self):
        if len(self.actions)==0:
            raise NoActionError('The form does not have any actions')
        for action in self.actions:
            if action.name in self.requestData.keys():
                return action.callback(self)
        return self.actions[0].callback(self)
            
        
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
        """ if we have request data then use it, if not then convert the data to request data unless it's a POST """
        if self._requestData is not None:
            return self._requestData
        if self.request.method =='POST':
            self.requestData = self.request.POST
        else:
            self._requestData = self.convertDataToRequestData()
        return self._requestData

    
    def _setRequestData(self, requestData):
        """ assign data """
        self._requestData = dottedDict(requestData)
        
    requestData = property(_getRequestData, _setRequestData)
    
    #
    # Getting the data from the form triggers a validation.
    #
    def _getData(self, raiseErrors=True):
        """ validate first and raise exceptions if necessary """
        r = self._getRequestData()
        data = convertRequestDataToData(self.structure, self._getRequestData(), errors=self.errors) 
        if raiseErrors:
            if len(self.errors.keys()) > 0:
                raise FormError('Tried to access data but conversion from request failed with %s errors (%s)'%(len(self.errors.keys()), self.errors.data))
        return dottedDict(data)
    
    def _getDefaults(self):
        return self._defaults
    
    def _setDefaults(self, data):
        """ assign data """
        self._defaults = data
        self._data = dottedDict(data)
        
    defaults = property(_getDefaults, _setDefaults)

    def validate(self):
        data = self._getData(raiseErrors=False)
        errors = validate(self.structure, data, errors=self.errors)
        if len(self.errors.keys()) > 0:
            raise FormError('Tried to access data but conversion from request failed with %s errors (%s)'%(len(errors.keys()), errors.data))
        return dottedDict(data)
        
    
    @property
    def fields(self):
        return self.structure.fields
            
            

