import schemaish

from webob import UnicodeMultiDict

from formish import util
from formish.dottedDict import dottedDict, isInt
from convertish.convert import *
from formish.validation import *
from formish.widgets import *
from formish.renderer import _default_renderer
from validatish import Required, validation_includes


class Action(object):
    """
    An action that that can added to a form.

    :arg callback: A callable with the signature (request, form, *args)
    :arg name: an valid html id used to lookup an action
    :arg label: The 'value' of the submit button and hence the text that people see
    """
    def __init__(self, callback, name, label):
        if not util.valid_identifier(name):
            raise FormError('Invalid action name %r.'%name)
        self.callback = callback
        self.name = name
        if label is None:
            self.label = util.title_from_name(name)
        else:
            self.label = label

            
def _cssname(self):
    """ Returns a hyphenated identifier using the form name and field name """
    return '%s-%s'%(self.form.name, '-'.join(self.name.split('.')))    


def _classes(self):
    """ Works out a list of classes that should be applied to the field """
    classes = [
        'field',
        self.attr.__class__.__name__.lower(),
        ]
    if self.widget is not None:
        classes.append(self.widget.__class__.__name__.lower())
    else:
        classes.append('defaultwidget')
    if self.required:
        classes.append('required')
    if self.widget is not None and self.widget.cssClass:
        classes.append(self.widget.cssClass)
    if self.error:
        classes.append('error')
    return ' '.join(classes)
            

def starify(name):
    """
    Replace any ints in a dotted key with stars. Used when applying defaults and widgets to fields
    """
    newname = []
    for key in name.split('.'):
        if isInt(key):
            newname.append('*')
        else:
            newname.append(key)
    name = '.'.join(newname)
    return name

class Field(object):
    """
    A wrapper for a schema field type that includes form information.
    
    The Schema Type Atribute does not have any bindings to the form library, it can be
    used on it's own. We bind the Schema Attribute to a Field in order to include form
    related information.

    :method __call__: returns a serialisation for this field using the form's renderer - read only
    
    """
    type = 'field'
    def __init__(self, name, attr, form):
        """
        :arg name: Name for the field
        :arg attr: Schema attr to bind to the field
        :type attr:  schemaish.attr.*
        :param form: The form the field belongs to.
        :type form: formish.Form instance.
        """
        self.name = name
        self.attr = attr
        self.form = form

    @property
    def title(self):
        """ The Field schema's title """
        try:
            return self.form.get_item_data(self.name,'title')
        except KeyError:
            if self.attr.title is not None:
                return self.attr.title
            else:
                return util.title_from_name(self.name.split('.')[-1])


    @property
    def description(self):
        """ The Field schema's description """
        try:
            return self.form.get_item_data(self.name,'description')
        except KeyError:
            return self.attr.description        


    @property
    def cssname(self):
        """ cssname identifier for the field """
        return _cssname(self)


    @property
    def classes(self):
        """ Works out a list of classes that should be applied to the field """
        return _classes(self)
  

    @property
    def value(self):
        """Convert the request_data to a value object for the form or None."""
        if '*' in self.name:
            return ['']
        return self.form.request_data.get(self.name,None)


    @property 
    def required(self):
        """ Does this field have a Not Empty validator of some sort """
        return validation_includes(self.attr.validator, Required)


    @property
    def error(self):
        """ Lazily get the error from the form.errors when needed """
        return self.form.errors.get(self.name, None)


    @property
    def widget(self):
        """ return the fields widget bound with extra params. """
        # Loop on the name to work out if any '*' widgets are used
        try:
            w = self.form.get_item_data(starify(self.name),'widget')
        except KeyError:
            w = Input()
        return w
        

    def __call__(self):
        """ returns a serialisation for this field using the form's renderer """
        return self.form.renderer('/formish/Field.html',{'f':self})
            
    

class Collection(object):
    """
    A wrapper for a schema group type that includes form information.

    The Schema structure does not have any bindings to the form library, it can
    be used on it's own. We bind the schema Structure Attribute to a Group
    which includes form information.
    """    


    def __init__(self, name, attr, form):
        """
        :arg name: Name for the Collection 
        :arg attr: Schema attr to bind to the field
        :type attr:  schemaish.attr.*
        :param form: The form the field belongs to.
        :type form: formish.Form instance.
        """
        self.name = name
        self.attr = attr
        self.form = form
        self._fields = {}    
        # Construct a title
        self.title = self.attr.title
        if self.title is None and name is not None:
            self.title = util.title_from_name(self.name.split('.')[-1])


    @property
    def description(self):
        """ Returns the schema's description """
        return self.attr.description        


    @property
    def cssname(self):
        """ Works out a list of classes that can be applied to the field """        
        return _cssname(self)
    

    @property
    def classes(self):
        """ Works out a list of classes that can be applied to the field """        
        return _classes(self)           
   

    @property
    def value(self):
        """Convert the request_data to a value object for the form or None."""
        return self.form.request_data.get(self.name,[''])
   

    @property 
    def required(self):
        """ Does this field have a Not Empty validator of some sort """
        return validation_includes(self.attr.validator, Required)


    @property
    def defaults(self):
        """Get the defaults from the form."""
        defaults = self.form.defaults.get(self.name,None)
        return defaults


    @property
    def error(self):
        """ Lazily get the error from the form.errors when needed """
        return self.form.errors.get(self.name, None)


    @property
    def widget(self):
        """ return the fields widget bound with extra params. """
        
        try:
            w = self.form.get_item_data(starify(self.name),'widget')
        except KeyError:
            w = SequenceDefault()
        return w


    def get_field(self, segments):
        for field in self.fields:
            if field.name.split('.')[-1] == segments[0]:
                if isinstance(field, Field):
                    return field
                else:
                    return field.get_field(segments[1:])


    def __getitem__(self, key):
        return FormAccessor(self.form, '%s.%s'%(self.name,key))


    @property
    def attrs(self):
        """ The schemaish attrs below this collection """
        return self.attr.attrs


    @property
    def fields(self):
        """ 
        Iterate through the fields, lazily bind the schema to the fields
        before returning.
        """
        for attr in self.attr.attrs:
            yield self.bind(attr[0], attr[1])        


    def bind(self, attr_name, attr):
        """ 
        return cached schema as a field; Otherwise bind the attr to a
        Group or Field as appropriate and store on the _fields cache
        
        :param attr_name:     Form Field/Group identifier
        :type attr_name:      Python identifier string
        :param attr:          Attribute to bind
        :type attr:           Schema attribute
        """
        try:
            return self._fields[attr_name]
        except KeyError:
            if self.name is None:
                keyprefix = attr_name
            else:
                keyprefix = '%s.%s'%(self.name,attr_name)
                
            if isinstance(attr, schemaish.Sequence):
                f = Sequence(keyprefix, attr, self.form)
            elif isinstance(attr, schemaish.Structure):
                f = Group(keyprefix, attr, self.form)
            else:
                f = Field(keyprefix, attr, self.form)
            self._fields[attr_name] = f
            return f


    def __call__(self):
        return self.form.renderer('/formish/Field.html',{'f':self})


    def __repr__(self):
        return '<formish %s name="%s">'%(self.type, self.name)
   


class Group(Collection):
    type = 'group'
    _template='structure'



class Sequence(Collection):
    type = 'sequence'
    _template = 'ssequence'


    @property
    def fields(self):
        """ 
        For sequences we check to see if the name is numeric. As names cannot be numeric normally, the first iteration loops 
        on a fields values and spits out a 
        """
        
        # Work out how many fields are in the sequence.
        # XXX We can't use self.form.request_data here because to build the
        # request_data we need to recurse throught the fields ... which calls
        # Sequence.fields ... which tries to build the request data ... which
        # calls Sequence.fields, etc, etc. Bang!
        if self.form._request_data:
            v = self.form._request_data.get(self.name, [])
        else:
            v = self.defaults

        if v is None:
            num_fields = 0
        else:
            num_fields = len(v)
            
        min=None
        max=None
        if self.widget is not None:
            min = getattr(self.widget, 'min', None)
            max = getattr(self.widget, 'max', None)
        if min is not None and num_fields < min:
            num_fields = min
        elif max is not None and num_fields > max:
            num_fields = max


        for n in xrange(num_fields):
            f = self.bind(n, self.attr.attr)
            yield f
            
    @property
    def template(self):
        return self.bind('*',self.attr.attr)
            


    

class Form(object):
    """
    The definition of a form

    The Form type is the container for all the information a form needs to
    render and validate data.

    :var name: The name of the form, used to namespace classes and ids
    :var defaults: Property to allow getting and setting of defaults
    :var error: Used to indicate a non field specific error on the form. None
                if no error
    """    

    renderer = _default_renderer

    _element_name = None
    _name = None

    _request_data = None

    def __init__(self, structure, name=None, defaults={}, errors={},
            action_url=None, renderer=None):
        """
        Create a new form instance

        :arg structure: Schema Structure attribute to bind to the the form
        :type structure: schemaish.Structure

        :arg name: Optional form name used to identify multiple forms on the same page
        :type name: str "valid html id"
            
        :arg defaults: Default values for the form
        :type defaults: dict

        :arg errors: Errors to store on the form for redisplay
        :type errors: dict

        :arg action_url: Use if you don't want the form to post to itself
        :type action_url: string "url or path"

        :arg renderer: Something that returns a form serialization when called
        :type renderer: callable


        """
        # allow a single schema items to be used on a form
        if not isinstance(structure, schemaish.Structure):
            structure = schemaish.Structure([structure])
        self.structure = Group(None, structure, self)
        self.item_data = {}
        self.name = name
        self.defaults = defaults
        self.errors = dottedDict(errors)
        self.error = None
        self.actions = []
        self.action_url = action_url
        if renderer is not None:
            self.renderer = renderer

    def element_name():
        """
        property to use when dealing with restish elements
        """
        def get(self):
            return self._element_name
        def set(self, name):
            if self._name is not None:
                raise Exception("Named forms cannot be used as elements.")
            self._element_name = name
        return property(get, set)
    element_name = element_name()

    def name():
        """
        The name of the form, used to namespace classes and ids
        """
        def get(self):
            if self._element_name is not None:
                return self._element_name
            if self._name is not None:
                return self._name
            return 'formish'
        def set(self, name):
            if self._element_name is not None:
                raise Exception("Named forms cannot be used as elements.")
            self._name = name
        return property(get, set)
    name = name()

    def add_action(self, callback, name="submit", label=None):
        """ 
        Add an action callable to the form

        :arg callback: A function to call if this action is triggered
        :type callback: callable

        :arg name: The identifier for this action
        :type name: string

        :arg label: Use this label instead of the form.name for the value of
            the action (for buttons, the value is used as the text on the button)
        :type label: string
        
        """
        if name in [action.name for action in self.actions]:
            raise ValueError('Action with name %r already exists.' % name)
        self.actions.append( Action(callback, name, label) )              

    def action(self, request, *args):
        """
        Find and call the action callback for the action found in the request

        :arg request: request which is used to find the action and also passed through to
            the callback
        :type request: webob.Request

        :arg args: list of arguments Pass through to the callback
        """
        if len(self.actions)==0:
            raise NoActionError('The form does not have any actions')
        for action in self.actions:
            if action.name in request.POST.keys():
                return action.callback(request,self, *args)
        return self.actions[0].callback(request, self, *args)


    def get_unvalidated_data(self, request_data, raise_exceptions=True):
        """
        Convert the request object into a nested dict in the correct structure
        of the schema but without applying the schema's validation.

        :arg request_data: Webob style request data
        :arg raise_exceptions: Whether to raise exceptions or return errors
        """
        data = convert_request_data_to_data(self.structure, request_data, errors=self.errors) 
        if raise_exceptions and len(self.errors.keys()):
            raise FormError('Tried to access data but conversion from request failed with %s errors (%s)'%(len(self.errors.keys()), self.errors.data))
        return data
    

    def _get_request_data(self):
        """
        Retrieve previously set request_data or return the defaults in
        request_data format.
        """
        if self._request_data is not None:
            return self._request_data
        self._request_data = convert_data_to_request_data(self.structure, dottedDict(self.defaults))
        return self._request_data


    def _set_request_data(self, request_data):
        """ 
        Assign raw request data to the form
        
        :arg request_data: raw request data (e.g. request.POST)
        :type request_data: Dictionary (dotted or nested or dottedDict or MultiDict)
        """
        self._request_data = dottedDict(request_data)


    request_data = property(_get_request_data, _set_request_data)
    
    
    def _getDefaults(self):
        """ Get the raw default data """
        return dottedDict(self._defaults)
   

    def _setDefaults(self, data):
        """ assign data """
        self._defaults = data
        self._request_data = None
   

    defaults = property(_getDefaults, _setDefaults)
    

    def validate(self, request, failure_callable=None, success_callable=None):
        """ 
        Get the data without raising exceptions and then validate the data. If
        there are errors, raise them; otherwise return the data
        """
        # If we pass in explicit failure and success callables then do this first
        if failure_callable is not None and success_callable is not None:
            return self._validate_and_call(raw_request, failure_callable=None, success_callable=None)
        self.errors = {}
        # Check this request was POSTed by this form.
        if not request.method =='POST' and request.POST.get('__formish_form__',None) == self.name:
            raise Exception("request does not match form name")
        
        requestPOST = UnicodeMultiDict(request.POST, encoding=util.getPOSTCharset(request))
        # Remove the sequence factory data from the request
        for k in requestPOST.keys():
            if '*' in k:
                requestPOST.pop(k)
        # We need the _request_data to be populated so sequences know how many
        # items they have (i.e. .fields method on a sequence uses the number of
        # values on the _request_data)
        self._request_data = dottedDict(requestPOST)
        self.request_data = pre_parse_request_data(self.structure,dottedDict(requestPOST))
        data = self.get_unvalidated_data(self.request_data, raise_exceptions=False)
        self._request_data = dottedDict(requestPOST)
        try:
            self.structure.attr.validate(data)
        except schemaish.attr.Invalid, e:
            for key, value in e.error_dict.items():
                if not self.errors.has_key(key):
                    self.errors[key] = value
        if len(self.errors.keys()) > 0:
            err_msg = 'Tried to access data but conversion from request failed with %s errors'
            raise FormError(err_msg%(len(self.errors.keys())))
        return data

    def _validate_and_call(self, raw_request, failure_callable=None, success_callable=None):
        try: 
            data = self.validate(raw_request)
        except FormError, e:
            return failure_callable(request, self)
        return success_callable(request, data)
 


    def set_item_data(self, key, name, value):
        """
        Allow the setting os certain attributes on item_data, a dictionary used
        to associates data with fields.
        """
        
        allowed = ['title','widget','description']
        if name in allowed:
            self.item_data.setdefault(key, {})[name] = value
        else:
            raise KeyError('Cannot set data onto this attribute')


    def get_item_data(self, key, name):
        """
        Access item data associates with a field key and an attribute name
        (e.g. title, widget, description')
        """
        return self.item_data.get(key, {})[name]


    def get_item_data_values(self, name):
        d = dottedDict({})
        for k,v in self.item_data:
            if v.has_key(name):
                d[k] = v[name]
        return d


    def __getitem__(self, key):
        return FormAccessor(self, key)


    @property
    def fields(self):
        """
        Return a generator that yields all of the fields at the top level of
        the form (e.g. if a field is a subsection or sequence, it will be up to
        the application to iterate that field's fields.
        """
        return self.structure.fields


    def get_field(self, name):
        """
        Get a field by dotted field name

        :arg name: Dotted name e.g. names.0.firstname
        """
        segments = name.split('.')
        for field in self.fields:
            if field.name.split('.')[-1] == segments[0]:
                if isinstance(field, Field):
                    return field
                else:
                    return field.get_field(segments[1:])


    def __call__(self):
        """
        Calling the Form generates a serialisation using the form's renderer
        """
        return self.renderer('/formish/Form.html',{'form':self})
        
    
    
class FormAccessor(object):
    """
    Helps in setting item_data on a form

    :arg form: The form instance we're setting data on 
    :arg key: The dotted key of the field we want to set/get an attribute on e.g. ['x.y']
    :arg prefix: A prefix used internally for recursion and allowing ['x']['y'] type access
    """

    def __init__(self, form, key, prefix=None):
        self.__dict__['form'] = form
        if prefix is not None:
            self.__dict__['key'] = '%s.%s'%(prefix,key)
        else:
            self.__dict__['key'] = key

    def __setattr__(self, name, value):
        self.form.set_item_data(self.key, name, value)

    def __getattr__(self, name):
        field = self.form.get_field(self.key)
        if name == 'field':
            return field
        else:
            return getattr(field, name)
    
    def __getitem__(self, key):
        return FormAccessor(self.form, key, prefix=self.key)
    
        
