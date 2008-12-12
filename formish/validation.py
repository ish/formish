import re
from formish.dottedDict import dottedDict
from validatish import Invalid
from convertish import convert

def convert_sequences(d):
    if not hasattr(d,'keys'):
        return d
    try:
        k = int(d.keys()[0])
    except ValueError:
        return dottedDict(d)
    intkeys = []
    for key in d.keys():
        intkeys.append(int(key))
    intkeys.sort()
    out = []
    for key in intkeys:
        out.append(d[str(key)])
    return out

def recursive_convert_sequences(d):
    if not hasattr(d,'keys'):
        return d
    if len(d.keys()) == 0:
        return d
    try:
        k = int(d.keys()[0])
    except ValueError:
        tmp = {}
        for k, v in d.items():
            tmp[k] = recursive_convert_sequences(v)
        return tmp
    intkeys = []
    for key in d.keys():
        intkeys.append(int(key))
    intkeys.sort()
    out = []
    for key in intkeys:
        out.append(recursive_convert_sequences(d[str(key)]))
    return out

def getNestedProperty(d,dottedkey):
    if dottedkey == '':
        return d
    keys = dottedkey.split('.')
    firstkey = keys[0]
    remaining_dottedkey = '.'.join(keys[1:])
    try:
        firstkey = int(firstkey)
    except:
        pass
    try:
        return getNestedProperty(d[firstkey],remaining_dottedkey)
    except (KeyError, IndexError):
        return None

def validate(structure, request_data, errors=None, keyprefix=None):
    """ Take a schemaish structure and use it's validators to return any errors"""
    if errors is None:
        errors = dottedDict()
    # Validate each field in the schema, return 
    # a dictionary of errors keyed by field name
    for attr in structure.attrs:
        # function is recursive so we have to build up a full key
        if keyprefix is None:
            newprefix = attr[0]
        else:
            newprefix = '%s.%s'%(keyprefix,attr[0])
        try:
            if hasattr(attr[1],'attrs'):
                validate(attr[1], request_data, errors=errors, keyprefix=newprefix)
            else: 
                if request_data.has_key(newprefix):
                    c = convert_sequences(request_data[newprefix])
                    attr[1].validate(c)
        except (Invalid, FieldValidationError), e:
            errors[newprefix] = e
    return errors

def convert_data_to_request_data(formStructure, data, request_data=None, errors=None):
    """ Take a form structure and use it's widgets to convert data to request data """
    if request_data is None:
        request_data = dottedDict()
    if errors is None:
        errors = dottedDict()
    for field in formStructure.fields:
        try:
            if field.type is 'group' or (field.type is 'sequence' and (field.widget is None or field.widget.converttostring is False)):
                convert_data_to_request_data(field, data, request_data=request_data, errors=errors)
            else:
                d = getNestedProperty(data, field.name)
                request_data[field.name] = field.widget.pre_render(field.attr,d)
        except Invalid, e:
            errors[field.name] = e
            raise
    return request_data
        
def convert_request_data_to_data(formStructure, request_data, data=None, errors=None):
    """ Take a form structure and use it's widgets to convert data to request data """
    
    if data is None:
        data = {}
    if errors is None:
        errors = {}

    for field in formStructure.fields:
        try:
            if field.type is 'group' or (field.type == 'sequence' and (field.widget is None or field.widget.converttostring is False)):
                if field.type == 'sequence':
                    # Make sure we have an empty field at least. If we don't do this and there are no items in the list then this key wouldn't appear.
                    data[field.name] = []
                convert_request_data_to_data(field, request_data, data=data, errors=errors)
            else: 
                # This needs to be cleverer... 
                data[field.name] = field.widget.convert(field.attr,request_data.get(field.name,[]))
        except convert.ConvertError, e:
            errors[field.name] = e
            
    data = recursive_convert_sequences(dottedDict(data))
    return data

def pre_parse_request_data(formStructure, request_data, data=None):
    if data is None:
        data = {}
    for field in formStructure.fields:
        if field.type is 'group' or (field.type == 'sequence' and field.widget is None):
            pre_parse_request_data(field, request_data, data=data)
        else: 
            # This needs to be cleverer...
            d = request_data.get(field.name,[])
            data[field.name] = field.widget.pre_parse_request(field.attr,d)
    return dottedDict(data)


class FormishError(Exception):
    """
    Base class for all Forms errors. A single string, message, is accepted and
    stored as an attribute.
    
    The message is not passed on to the Exception base class because it doesn't
    seem to be able to handle unicode at all.
    """
    def __init__(self, message, *a):
        Exception.__init__(self, message, *a)
        self.message = message
    def __str__(self):
        return self.message
    __unicode__ = __str__


class FormError(FormishError):
    """
    Form validation error. Raise this, typically from a submit callback, to
    signal that the form (not an individual field) failed to validate.
    """
    pass

    
class NoActionError(FormishError):
    """
    Form validation error. Raise this, typically from a submit callback, to
    signal that the form (not an individual field) failed to validate.
    """
    pass
    
    
class FieldError(FormishError):
    """
    Base class for field-related exceptions. The failure message and the failing
    field name are stored as attributes.
    """
    def __init__(self, message, fieldName=None):
        FormishError.__init__(self, message, fieldName)
        self.fieldName = fieldName


class FieldValidationError(FieldError):
    """
    Exception that signals that a field failed to validate.
    """
    pass
    
    
class FieldRequiredError(FieldValidationError):
    """
    Exception that signals that a field that is marked as required was not
    entered.
    """
    pass

