"""
The form module contains the main form, field, group and sequence classes
"""

import re

from peak.util.proxies import ObjectWrapper
from webob import UnicodeMultiDict

import schemaish, validatish
from formish import util
from dottedish import dotted, is_int
from formish import validation
from formish import widgets
from formish.renderer import _default_renderer

NOARG = object()

class Action(object):
    """
    An action that that can added to a form.

    :arg callback: A callable with the signature (request, form, *args)
    :arg name: an valid html id used to lookup an action
    :arg label: The 'value' of the submit button and hence the text that people see
    """
    def __init__(self, callback, name, label):
        if not util.valid_identifier(name):
            raise validation.FormError('Invalid action name %r.'% name)
        self.callback = callback
        self.name = name
        if label is None:
            self.label = util.title_from_name(name)
        else:
            self.label = label

            
def _cssname(self):
    """ Returns a hyphenated identifier using the form name and field name """
    return '%s-%s'% (self.form.name, '-'.join(self.name.split('.')))    


def _classes(self):
    """ Works out a list of classes that should be applied to the field """
    classes = [
        'field',
        re.sub('[0-9\*]+','n',_cssname(self)),
        'type-%s'%self.attr.type.lower(),
        ]
    classes.append('widget-%s'%self.widget.type.lower())
    if self.required:
        classes.append('required')
    if self.widget.css_class is not None:
        classes.append(self.widget.css_class)
    if str(self.error):
        classes.append('error')
    if getattr(self,'contains_error',None):
        classes.append('contains-error')
    return ' '.join(classes)
            

def starify(name):
    """
    Replace any ints in a dotted key with stars. Used when applying defaults and widgets to fields
    """
    newname = []
    for key in name.split('.'):
        if is_int(key):
            newname.append('*')
        else:
            newname.append(key)
    name = '.'.join(newname)
    return name


def fall_back_renderer(renderer, name, widget, vars):
    import mako
    try:
        return renderer('/formish/widgets/%s/%s.html'%(widget,name), vars)
    except mako.exceptions.TopLevelLookupException, e:
        return renderer('/formish/%s.html'%(name), vars)
    

class TemplatedString(object):
    """
    A callable, teplated string
    """
    def __init__(self, obj, attr_name, val):
        self.obj = obj
        self.attr_name = attr_name
        self.val = val

    def __str__(self):
        if not self.val:
            return ''
        return unicode(self.val)

    def __repr__(self):
        if not self.val:
            return ''
        return unicode(self.val)
        

    def __nonzero__(self):
        if self.val:
            return True
        else:
            return False

    def __call__(self):
        widget_type, widget = self.obj.widget.template.split('.')
        renderer = self.obj.form.renderer
        name = '%s/%s'%(widget_type,self.attr_name)
        vars = {'field':self.obj}
        return fall_back_renderer(renderer, name, widget, vars)



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

    def __repr__(self):
        return 'formish.Field(name=%r, attr=%r)'% (self.name, self.attr)

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
            val =  self.form.get_item_data(self.name,'description')
        except KeyError:
            val = self.attr.description        
        return TemplatedString(self, 'description', val)


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
            return  self.widget.to_request_data(self.attr, self.defaults)
        return self.form.request_data.get(self.name, None)


    @property 
    def required(self):
        """ Does this field have a Not Empty validator of some sort """
        return validatish.validation_includes(self.attr.validator, validatish.Required)


    @property
    def defaults(self):
        """Get the defaults from the form."""
        if '*' not in self.name:
            defaults = self.form.defaults.get(self.name, None)
        else:
            defaults = self.form.get_item_data(self.name, 'default', None)
        return defaults

    @property
    def error(self):
        """ Lazily get the error from the form.errors when needed """
        error = self.form.errors.get(self.name, None)
        if error is not None:
            val = str(error)
        else: 
            val = ''
        return TemplatedString(self, 'error', val)

    @property
    def errors(self):
        """ Lazily get the error from the form.errors when needed """
        return self.form.errors.get(self.name, None)

    @property
    def widget(self):
        """ return the fields widget bound with extra params. """
        # Loop on the name to work out if any '*' widgets are used
        try:
            widget_type = self.form.get_item_data(starify(self.name),'widget')
        except KeyError:
            widget_type = widgets.Input()
        return BoundWidget(widget_type, self)

        

    def __call__(self):
        """ returns a serialisation for this field using the form's renderer """
        widget_type, widget = self.widget.template.split('.')
        renderer = self.form.renderer
        name = 'field/main'
        vars = {'field':self}
        return fall_back_renderer(renderer, name, widget, vars)
            
    def label(self):
        widget_type, widget = self.widget.template.split('.')
        """ returns the templated title """
        renderer = self.form.renderer
        name = 'field/label'
        vars = {'field':self}
        return fall_back_renderer(renderer, name, widget, vars)
    
    def inputs(self):
        """ returns the templated widget """
        widget_type, widget = self.widget.template.split('.')
        renderer = self.form.renderer
        name = 'field/inputs'
        vars = {'field':self}
        return fall_back_renderer(renderer, name, widget, vars)



class CollectionFieldsWrapper(ObjectWrapper):
    """
    Allow fields attr of a form to be accessed (as a generator) but also callable
    """
    collection = None
    def __init__(self, collection):
        ObjectWrapper.__init__(self, iter(collection.collection_fields()))
        self.collection = collection

    def __call__(self):
        widget_type, widget = self.collection.widget.template.split('.')
        renderer = self.collection.form.renderer
        name = '%s/fields'%widget_type
        vars = {'field':self.collection}
        return fall_back_renderer(renderer, name, widget, vars)


class Collection(object):
    """
    A wrapper for a schema group type that includes form information.

    The Schema structure does not have any bindings to the form library, it can
    be used on it's own. We bind the schema Structure Attribute to a Group
    which includes form information.
    """    
    type = None


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
    def template_type(self):
        """ Returns the template type to use for this item """
        if self.attr.type == 'Structure':
            name = 'structure'
        elif self.attr.type == 'Sequence' and self.widget.type == 'SequenceDefault':
            name = 'sequence' 
        else:
            name = 'field'
        return name


    @property
    def description(self):
        """ Returns the schema's description """
        val = self.attr.description        
        return TemplatedString(self,'description',val)


    @property
    def cssname(self):
        """ Works out a list of classes that can be applied to the field """
        return _cssname(self)
    

    @property
    def classes(self):
        """
        Works out a list of classes that can be applied to the field """
        return _classes(self)           
   

    @property
    def value(self):
        """Convert the request_data to a value object for the form or None."""
        return self.form.request_data.get(self.name, [''])
   

    @property 
    def required(self):
        """ Does this field have a Not Empty validator of some sort """
        return validatish.validation_includes(self.attr.validator, validatish.Required)


    @property
    def defaults(self):
        """Get the defaults from the form."""
        defaults = self.form.defaults.get(self.name, None)
        return defaults


    @property
    def error(self):
        """ Lazily get the error from the form.errors when needed """
        val = self.form.errors.get(self.name, None)
        return TemplatedString(self, 'error', val)

    @property
    def errors(self):
        """ Lazily get the error from the form.errors when needed """
        return self.form.errors.get(self.name, None)

    @property
    def contains_error(self):
        """ Check to see if any child elements have errors """
        for k in self.form.errors.keys():
            if k.startswith(self.name):
                return True
        return False

    @property
    def widget(self):
        """ return the fields widget bound with extra params. """
        
        try:
            widget_type = BoundWidget(self.form.get_item_data(starify(self.name),'widget'),self)
        except KeyError:
            widget_type = BoundWidget(widgets.SequenceDefault(),self)
        return widget_type


    def get_field(self, segments):
        """ recursively get dotted field names """
        for field in self.fields:
            if field.name.split('.')[-1] == segments[0]:
                if isinstance(field, Field):
                    return field
                else:
                    return field.get_field(segments[1:])


    def __getitem__(self, key):
        return FormAccessor(self.form, '%s.%s'% (self.name, key))


    @property
    def attrs(self):
        """ The schemaish attrs below this collection """
        return self.attr.attrs

    def collection_fields(self):
        for attr in self.attrs:
            yield self.bind(attr[0], attr[1])        
        

    @property
    def fields(self):
        """ 
        Iterate through the fields, lazily bind the schema to the fields
        before returning.
        """
        return CollectionFieldsWrapper(self)


    def bind(self, attr_name, attr):
        """ 
        return cached bound schema as a field; Otherwise bind the attr to a
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
                keyprefix = '%s.%s'% (self.name, attr_name)
                
            if isinstance(attr, schemaish.Sequence):
                bound_field = Sequence(keyprefix, attr, self.form)
            elif isinstance(attr, schemaish.Structure):
                bound_field = Group(keyprefix, attr, self.form)
            else:
                bound_field = Field(keyprefix, attr, self.form)
            self._fields[attr_name] = bound_field
            return bound_field





    def __call__(self):
        """ returns a serialisation for this field using the form's renderer """
        widget_type, widget = self.widget.template.split('.')
        renderer = self.form.renderer
        name = '%s/main'%widget_type
        vars = {'field':self}
        return fall_back_renderer(renderer, name, widget, vars)
            
    def label(self):
        """ returns the templated title """
        widget_type, widget = self.widget.template.split('.')
        renderer = self.form.renderer
        name = '%s/label'%widget_type
        vars = {'field':self}
        return fall_back_renderer(renderer, name, widget, vars)
         
    def metadata(self):
        """ returns the metadata """
        widget_type, widget = self.widget.template.split('.')
        renderer = self.form.renderer
        name = '%s/metadata'%widget_type
        vars = {'field':self}
        return fall_back_renderer(renderer, name, widget, vars)

    def inputs(self):
        """ returns the templated widget """
        widget_type, widget = self.widget.template.split('.')
        renderer = self.form.renderer
        name = '%s/inputs'%widget_type
        vars = {'field':self}
        return fall_back_renderer(renderer, name, widget, vars)

    def __repr__(self):
        return 'formish.%s(name=%r, attr=%r)'% (self.type.title(), self.name, self.attr)

class Group(Collection):
    """
    A group is a basic collection with a different template
    """
    type = 'group'
    template = 'structure'



class Sequence(Collection):
    """
    A sequence is a collection with a variable number of fields depending on request data, data or min/max values
    """
    type = 'sequence'
    template = 'sequence'

    def collection_fields(self):
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
            data = self.form._request_data.get(self.name, [])
        else:
            data = self.defaults

        if data is None:
            num_fields = 0
        else:
            num_fields = len(data)
            
        minimum = None
        maximum = None
        if self.widget is not None:
            minimum = getattr(self.widget, 'min', None)
            maximum = getattr(self.widget, 'max', None)
        if minimum is not None and num_fields < min:
            num_fields = minimum
        elif max is not None and num_fields > max:
            num_fields = maximum


        for num in xrange(num_fields):
            field = self.bind(num, self.attr.attr)
            yield field
            
    @property
    def template(self):
        return self.bind('*', self.attr.attr)
            

class BoundWidget(object):
    """
    Because widget's need to be able to render themselves
    """   
    

    def __init__(self, widget, field):
        self.__dict__['widget'] = widget
        self.__dict__['field'] = field
     

    def __getattr__(self, name):
        return getattr(self.widget, name)

    def __setattr__(self, name, value):
        setattr(self.widget, name, value)

    def __call__(self):
        widget_type, widget = self.widget.template.split('.')
        return self.field.form.renderer('/formish/widgets/%s/widget.html'%widget, {'field':self.field})

    def __repr__(self):
        return 'BoundWidget(widget=%r, field=%r)'%(self.widget, self.field)

class FormFieldsWrapper(ObjectWrapper):
    """
    Allow fields attr of a form to be accessed (as a generator) but also callable
    """
    form = None
    def __init__(self, form):
        self.form = form
        ObjectWrapper.__init__(self, form.structure.fields)

    def __call__(self):
        return self.form.renderer('/formish/form/fields.html', {'form':self.form})
    

class Form(object):
    """
    The definition of a form

    The Form type is the container for all the information a form needs to
    render and validate data.
    """

    SUPPORTED_METHODS = ['GET', 'POST']

    renderer = _default_renderer

    _element_name = None
    _name = None

    _request_data = None

    def __init__(self, structure, name=None, defaults=None, errors=None,
            action_url=None, renderer=None, method='POST'):
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

        :arg method: Option method, default POST
        :type method: string
        """
        if method.upper() not in self.SUPPORTED_METHODS:
            raise ValueError("method must be one of GET or POST")
        # allow a single schema items to be used on a form
        if not isinstance(structure, schemaish.Structure):
            structure = schemaish.Structure([structure])
        self.structure = Group(None, structure, self)
        self.item_data = {}
        self.name = name
        if defaults is None:
            defaults = {}
        if errors is None:
            errors = {}
        self.defaults = defaults
        self.errors = dotted(errors)
        self.error = None
        self._actions = []
        self.action_url = action_url
        if renderer is not None:
            self.renderer = renderer
        self.method = method

    def __repr__(self):
        attributes = []
        attributes.append('%r'%self.structure.attr)
        attributes.append('name=%r'%self.name)
        if self.defaults.data != {}:
            attributes.append('defaults=%r'%self.defaults.data)
        if self.errors.data != {}:
            attributes.append('errors=%r'%self.errors.data)
        if self.action_url:
            attributes.append('action_url=%r'%self.action_url)
        return 'formish.Form(%s)'%( ', '.join(attributes) )

    def _element_name_get(self):
        """ Set the element name """
        return self._element_name

    def _element_name_set(self, name):
        """ Get the element name or raise an error """
        if self._name is not None:
            raise Exception("Named forms cannot be used as elements.")
        self._element_name = name

    element_name = property(_element_name_get, _element_name_set)

    def _name_get(self):
        """ Get the name of the form, default to `formish` """
        if self._element_name is not None:
            return self._element_name
        if self._name is not None:
            return self._name
        return 'form'

    def _name_set(self, name):
        """ Set the form name """ 
        if self._element_name is not None:
            raise Exception("Named forms cannot be used as elements.")
        self._name = name

    name = property(_name_get, _name_set)

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
        if name in [action.name for action in self._actions]:
            raise ValueError('Action with name %r already exists.'% name)
        self._actions.append( Action(callback, name, label) )              

    def action(self, request, *args):
        """
        Find and call the action callback for the action found in the request

        :arg request: request which is used to find the action and also passed through to
            the callback
        :type request: webob.Request

        :arg args: list of arguments Pass through to the callback
        """
        if len(self._actions)==0:
            raise validation.NoActionError('The form does not have any actions')
        request_data = getattr(request, self.method.upper())
        for action in self._actions:
            if action.name in request_data:
                return action.callback(request, self, *args)
        return self._actions[0].callback(request, self, *args)


    def get_unvalidated_data(self, request_data, raise_exceptions=True):
        """
        Convert the request object into a nested dict in the correct structure
        of the schema but without applying the schema's validation.

        :arg request_data: Webob style request data
        :arg raise_exceptions: Whether to raise exceptions or return errors
        """
        data = validation.from_request_data(self.structure, request_data, errors=self.errors) 
        if raise_exceptions and len(self.errors.keys()):
            raise validation.FormError( \
        'Tried to access data but conversion from request failed with %s errors (%s)'% \
                   (len(self.errors.keys()), self.errors.data))
        return data
    

    def _get_request_data(self):
        """
        Retrieve previously set request_data or return the defaults in
        request_data format.
        """
        if self._request_data is not None:
            return self._request_data
        self._request_data = validation.to_request_data(self.structure, dotted(self.defaults))
        return self._request_data


    def _set_request_data(self, request_data):
        """ 
        Assign raw request data to the form
        
        :arg request_data: raw request data (e.g. request.POST)
        :type request_data: Dictionary (dotted or nested or dotted or MultiDict)
        """
        self._request_data = dotted(request_data)


    request_data = property(_get_request_data, _set_request_data)
    
    
    def _get_defaults(self):
        """ Get the raw default data """
        return dotted(self._defaults)
   

    def _set_defaults(self, data):
        """ assign data """
        self._defaults = data
        self._request_data = None
   

    defaults = property(_get_defaults, _set_defaults)
    

    def validate(self, request, failure_callable=None, success_callable=None):
        """ 
        Validate the form data in the request.

        By default, this method returns either a dict of data or raises an
        exception if validation fails. However, if either success_callable or
        failure_callable are provided then the approriate callback will be
        called, and the callback's result will be returned instead.

        :arg request: the HTTP request
        :type request: webob.Request
        :arg failure_callable: Optional callback to call on failure.
        :arg success_callable: Optional callback to call on success.
        :returns: Python dict of converted and validated data.
        :raises: formish.FormError, raised on validation failure.
        """
        try: 
            data = self._validate(request)
        except validation.FormError, e:
            if failure_callable is None:
                raise
            else:
                return failure_callable(request, self)
        if success_callable is None:
            return data
        else:
            return success_callable(request, data)

    def _validate(self, request):
        """
        Get the data without raising exceptions and then validate the data. If
        there are errors, raise them; otherwise return the data
        """
        # XXX Should this happen after the basic stuff has happened?
        self.errors = {}
        # Decide what request data to use. The method will have been validated
        # already (unless someone's messing around!) so we can just use it in a
        # getattr.
        request_data = getattr(request, self.method.upper())
        # Check this request was submitted by this form.
        if request_data.get('__formish_form__') != self.name:
            raise Exception("request does not match form name")
        # Decode request data according to the request's charset.
        request_data = UnicodeMultiDict(request_data,
                                        encoding=util.get_post_charset(request))
        # Remove the sequence factory data from the request
        for k in request_data.keys():
            if '*' in k:
                request_data.pop(k)
        # We need the _request_data to be populated so sequences know how many
        # items they have (i.e. .fields method on a sequence uses the number of
        # values on the _request_data)
        self._request_data = dotted(request_data)
        self.request_data = validation.pre_parse_incoming_request_data( \
                    self.structure,dotted(request_data))
        data = self.get_unvalidated_data( \
                    self.request_data, raise_exceptions=False)
        try:
            self.structure.attr.validate(data)
        except schemaish.attr.Invalid, e:
            for key, value in e.error_dict.items():
                if key not in self.errors:
                    self.errors[key] = value
        if len(self.errors.keys()) > 0:
            err_msg = 'Tried to access data but conversion from request failed with %s errors'
            raise validation.FormError(err_msg% (len(self.errors.keys())))
        return data

    def set_item_data(self, key, name, value):
        """
        Allow the setting os certain attributes on item_data, a dictionary used
        to associates data with fields.
        """
        allowed = ['title', 'widget', 'description','default']
        if name in allowed:
            if name == 'default' and '*' not in key:
                self.defaults[key] = value
            else:
                self.item_data.setdefault(key, {})[name] = value
        else:
            raise KeyError('Cannot set data onto this attribute')


    def get_item_data(self, key, name, default=NOARG):
        """
        Access item data associates with a field key and an attribute name
        (e.g. title, widget, description')
        """
        if default is NOARG:
            data = self.item_data.get(key, {})[name]
        else:
            data = self.item_data.get(key, {}).get(name, default)
        return data


    def get_item_data_values(self, name=None):
        """
        get all of the item data values
        """
        data = dotted({})
        for key, value in self.item_data.items():
            if name is not None and value.has_key(name):
                data[key] = value[name]
            else:
                data[key] = value
        return data


    def __getitem__(self, key):
        return FormAccessor(self, key)



    @property
    def fields(self):
        """
        Return a generator that yields all of the fields at the top level of
        the form (e.g. if a field is a subsection or sequence, it will be up to
        the application to iterate that field's fields.
        """
        return FormFieldsWrapper(self)



    def get_field(self, name):
        """
        Get a field by dotted field name

        :arg name: Dotted name e.g. names.0.firstname
        """
        segments = name.split('.')
        for field in self.fields:
            if field.name.split('.')[-1] == segments[0]:
                if len(segments) == 1:
                    return field
                else:
                    return field.get_field(segments[1:])


    def __call__(self):
        """
        Calling the Form generates a serialisation using the form's renderer
        """
        return self.renderer('/formish/form/main.html', {'form':self})

    def header(self):
        """ Return just the header part of the template """
        return self.renderer('/formish/form/header.html', {'form':self})
        
    def footer(self):
        """ Return just the footer part of the template """
        return self.renderer('/formish/form/footer.html', {'form':self})
        
    def metadata(self):
        """ Return just the metada part of the template """
        return self.renderer('/formish/form/metadata.html', {'form':self})

    def actions(self):
        """ Return just the actions part of the template """
        return self.renderer('/formish/form/actions.html', {'form':self})

        
   


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
            self.__dict__['key'] = '%s.%s'% (prefix, key)
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

    def __call__(self):
        return self.form.get_field(self.key)()
    
        
