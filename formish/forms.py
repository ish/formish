import copy
from webhelpers.html import literal
from restish import templating
import schemaish

from formish import util
from formish.dottedDict import dottedDict
from formish.converter import *
from formish.validation import *
from formish.widgets import *


class Action(object):
    """ Tracks an action that has been added to a form. """
    def __init__(self, callback, name, label):

        if not util.valid_identifier(name):
            raise FormError('Invalid action name %r.'%name)

        self.callback = callback
        self.name = name
        if label is None:
            self.label = util.titleFromName(name)
        else:
            self.label = label

            
def _cssname(self):
    """ Returns a hyphenated identifier using the form name and field name """
    return '%s-%s'%(self.form.name, '-'.join(self.name.split('.')))    


def _classes(self):
    """ Works out a list of classes that can be applied to the field """
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
            

def _required(self):
    """ Does this field have a Not Empty validator of some sort """
    hasrequiredvalidator = _isNotEmpty(self, self.attr.validator)
    return hasrequiredvalidator


def _isNotEmpty(self,validator):
    """ parses through validators to work out if there is a not empty validator """
    if validator is None:
        return False
    if isinstance(validator, schemaish.NotEmpty) or getattr(validator,'not_empty'):
        return True
    if hasattr(validator,'validators'):
        for v in validator.validators:
            self._isNotEmpty(v)
    return False


class Field(object):
    """
    A wrapper for a schema field type that includes form information.
    
    The Schema Type Atribute does not have any bindings to the form library, it can be
    used on it's own. We bind the Schema Attribute to a Field in order to include form
    related information.
    
    The _widget attribute is a base widget to which the real widget is bound 
    """

    def __init__(self, name, attr, form):
        """
        @param name:            Fields dotted name
        @type name:             String
        @param attr:            a Schema attr to bind to the field
        @type attr:             Schema Attribute object
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
        """ Works out a list of classes that can be applied to the field """
        return _cssname(self)
    
    @property
    def classes(self):
        """ Works out a list of classes that can be applied to the field """
        return _classes(self)
   
    @property 
    def required(self):
        """ Does this field have a Not Empty validator of some sort """
        return _required(self)
        
    @property
    def description(self):
        """ Description attribute """
        return self.attr.description        
        
    @property
    def data(self):
        """ Lazily get the data from the form.data when needed """
        return self.form.data[self.name]
    
    @property
    def _data(self):
        """ Lazily get the raw data from the form.data when needed """
        return self.form._data[self.name]
    
    @property
    def value(self):
        """Convert the requestData to a value object for the form or None."""
        return self.form._requestData.get(self.name, [None])
        
    @property
    def error(self):
        """ Lazily get the error from the form.errors when needed """
        return self.form.errors.get(self.name, None)
    
    def _getWidget(self):
        """ return the fields widget bound with extra params. """
        return BoundWidget(self._widget, self)
    
    def _setWidget(self, widget):
        """ Set the field widget. """
        self._widget = widget
        
    widget = property(_getWidget, _setWidget)
 
    def __call__(self):
        """Default template renderer for the field (not the widget itself) """
        return literal(templating.render(self.form._request, "formish/field.html", {'field': self}))
        

class Group(object):
    """
    A wrapper for a schema group type that includes form information.
    
    The Schema structure does not have any bindings to the form library, it can be
    used on it's own. We bind the schema Structure Attribute to a Group which includes form information.
    
    The _widget attribute is a base widget to which the real widget is bound 
    """    

    def __init__(self, name, attr, form):
        """
        @param name:            Group's dotted name
        @type name:             String
        @param attr:            a Schema attr to bind to the this group
        @type attr:             Schema Attribute object
        @param form:            The form the field belongs to.
        @type form:             Form instance.        
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
        """ Works out a list of classes that can be applied to the field """        
        return _cssname(self)
    
    @property
    def classes(self):
        """ Works out a list of classes that can be applied to the field """        
        return _classes(self)           
            
    @property 
    def required(self):
        """ Does this field have a Not Empty validator of some sort """
        return _required(self)

    @property
    def description(self):
        return self.attr.description        
        
    @property
    def attrs(self):
        return self.attr.attrs
    
    @property
    def fields(self):
        """ 
        If we iterate through the fields, lazily bind the schema to the fields
        before returning.
        """
        for attr in self.attr.attrs:
            yield self.bind(attr[0], attr[1])        
    
    def __getattr__(self, name):
        """
        When we try to get a child field, lazily bind the child to the schema
        for that child.
        """
        return self.bind( name, self.attr.get(name) )

    def bind(self, attr_name, attr):
        """ 
        return cached bound schema as a field; Otherwise bind the attr to a
        Group or Field as appropriate and store on the _fields cache
        
        @param attr_name:     Form Field/Group identifier
        @type attr_name:      Python identifier string
        @param attr:          Attribute to bind
        @type attr:           Schema attribute
        """
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
        
    def _getWidget(self):
        """ return the fields widget bound with extra params. """        
        return BoundWidget(self._widget, self)
    
    def _setWidget(self, widget):
        """ Set the field widget. """        
        self._widget = widget
        
    widget = property(_getWidget, _setWidget)   
    
    def __call__(self):
        """ Default template renderer for the group """
        return literal(templating.render(self.form._request, "formish/structure.html", {'group': self, 'fields': self.fields}))
    
    
class Form(object):
    """
    The Form type is the container for all the information a form needs to
    render and validate data.
    """    

    _request = None
    _requestData = None

    def __init__(self, name, structure, defaults=None, widgets=None, errors=None):
        """
        The form can be initiated with a set of data defaults (using defaults) or with some requestData. The requestData
        can be instantiated in order to set up a partially completed form with data that was persisted in some fashion.
        
        @param name:            Form name to be used in namespacing the form css and names
        @type name:             String
        @param structure:       a Schema Structure attribute to bind to the the form
        @type structure:        Schema Structure Attribute object
        @param defaults:        Defaults to override the standard form widget defaults
        @type defaults:         Dictionary (dotted or nested)
        @param widgets:         Widgets to use for form fields
        @type widgets:          Dictionary (dotted or nested)
        @param errors:          Errors to store on the form for redisplay
        @type errors:           Dictionary of validation error objects
        """
        self.name = name
        self.structure = Group(None, structure, self)
        self._data = dottedDict(defaults or {})
        self.errors = dottedDict(errors or {})
        self.actions = []
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
        """ 
        Add an action object to the form
        
        @param callback:       A function to call if this action is triggered
        @type callback:        Function or Method
        @param name:           The identifier for this action
        @type name:            Python identifier string
        @param label:          Use this label instead of the name for the value (label) of the action
        @type label:           String
        
        """
        if name in [action.name for action in self.actions]:
            raise ValueError('Action with name %r already exists.' % name)
        self.actions.append( Action(callback, name, label) )              

    def action(self, request):
        """ Find and call the action callback for the action used """
        if len(self.actions)==0:
            raise NoActionError('The form does not have any actions')
        for action in self.actions:
            if action.name in request.POST.keys():
                return action.callback(request, self)
        return self.actions[0].callback(request, self)
            
    def __call__(self, request):
        """ Render the form """
        # XXX Set the request and "request" data on the form while we're
        # rendering. This is just a nasty hack to make them available to the
        # groups and fields. Really, they should be passed in explicitly or by
        # using some sort of request-bound object (hint there's one in
        # restish.page already).
        self._request = request
        if request.method =='POST' and request.POST.get('__formish_form__') == self.name:
            self._requestData = dottedDict(request.POST)
        else:
            self._requestData = convertDataToRequestData(self.structure, self._data)
        result = literal(templating.render(request, "formish/form.html", {'form': self}))
        self._request = None
        self._requestData = None
        return result

    def __getattr__(self, name):
        return getattr( self.structure, name )
    
    def _getRequestData(self):
        """ if we have request data then use it, if not then convert the data to request data unless it's a POST from this form """
        if self._requestData is not None:
            return self._requestData
        # If we have posted data and this is the form that has been posted then set the request data
        if self.request.method =='POST' and self.request.POST.get('__formish_form__',None) == self.name:
            self.requestData = self.request.POST
        else:
            self._requestData = self.convertDataToRequestData()
        return self._requestData
    
    def _setRequestData(self, requestData):
        """ 
        Assign raw request data 
        
        @param requestData:     raw request data (e.g. request.POST)
        @type requestData:      Dictionary (dotted or nested or dottedDict or MultiDict)
        """
        self._requestData = dottedDict(requestData)
    
    def get_unvalidated_data(self, request_data, raiseErrors=True):
        """
        Convert the request object into a nested dict in the correct structure
        of the schema but without applying the schema's validation.
        """
        dotted_request_data = dottedDict(copy.deepcopy(request_data))
        data = convertRequestDataToData(self.structure, dotted_request_data, errors=self.errors) 
        if raiseErrors and len(self.errors.keys()):
            raise FormError('Tried to access data but conversion from request failed with %s errors (%s)'%(len(self.errors.keys()), self.errors.data))
        return dottedDict(data)
    
    def _getDefaults(self):
        """ Get the raw default data """
        return self._defaults
    
    def _setDefaults(self, data):
        """ assign data """
        self._defaults = data
        self._data = dottedDict(data)
        
    defaults = property(_getDefaults, _setDefaults)

    def validate(self, request):
        """ 
        Get the data without raising exception and then validate the data. If
        there are errors, raise them; otherwise return the data
        """
        # Check this request was POSTed by this form.
        if not request.method =='POST' and request.POST.get('__formish_form__',None) == self.name:
            raise Exception("request does not match form name")
        data = self.get_unvalidated_data(request.POST, raiseErrors=False)
        errors = validate(self.structure, data, errors=self.errors)
        if len(self.errors.keys()) > 0:
            raise FormError('Tried to access data but conversion from request failed with %s errors (%s)'%(len(errors.keys()), errors.data))
        return dottedDict(data)
        
    @property
    def fields(self):
        return self.structure.fields

