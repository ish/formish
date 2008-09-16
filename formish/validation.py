import re
import schemaish
from formish.dottedDict import dottedDict

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

def validate(structure, requestData, errors=None, keyprefix=None):   
    """ Take a schemaish structure and use it's validators to return any errors"""
    if errors is None:
        errors = dottedDict()
    # Use formencode to validate each field in the schema, return 
    # a dictionary of errors keyed by field name
    for attr in structure.attrs:
        if keyprefix is None:
            newprefix = attr[0]
        else:
            newprefix = '%s.%s'%(keyprefix,attr[0])
        try:
            if hasattr(attr[1],'attrs'):
                validate(attr[1], requestData, errors=errors, keyprefix=newprefix)
            else: 
                c = convert_sequences(requestData.get(newprefix,None))
                attr[1].validate(c)
        except (schemaish.Invalid, FieldValidationError), e:
            errors[newprefix] = e
    return errors

def convertDataToRequestData(formStructure, data, requestData=None, errors=None):
    """ Take a form structure and use it's widgets to convert data to request data """
    if requestData is None:
        requestData = dottedDict()
    if errors is None:
        errors = dottedDict()
    for field in formStructure.fields:
        try:
            if field.type is 'group' or (field.type is 'sequence' and field.widget is None):
                convertDataToRequestData(field, data, requestData=requestData, errors=errors)
            else:
                d = getNestedProperty(data, field.name)
                requestData[field.name] = field.widget.pre_render(field.attr,d)
        except schemaish.Invalid, e:
            errors[field.name] = e
            raise
    return requestData
        
def convertRequestDataToData(formStructure, requestData, data=None, errors=None):
    """ Take a form structure and use it's widgets to convert data to request data """
    
    if data is None:
        data = {}
    if errors is None:
        errors = {}

    for field in formStructure.fields:
        try:
            if field.type is 'group' or (field.type == 'sequence' and field.widget is None):
                if field.type == 'sequence':
                    # Make sure we have an empty field at least. If we don't do this and there are no items in the list then this key wouldn't appear.
                    data[field.name] = []
                convertRequestDataToData(field, requestData, data=data, errors=errors)
            else: 
                # This needs to be cleverer... 
                print 'converting ',field.name
                data[field.name] = field.widget.convert(field.attr,requestData.get(field.name,[]))
        except (schemaish.Invalid, FieldValidationError), e:
            errors[field.name] = e
            
    data = recursive_convert_sequences(dottedDict(data))
    return data

def preParseRequestData(formStructure, requestData, data=None):
    if data is None:
        data = {}
    for field in formStructure.fields:
        if field.type is 'group' or (field.type == 'sequence' and field.widget is None):
            preParseRequestData(field, requestData, data=data)
        else: 
            # This needs to be cleverer...
            d = requestData.get(field.name,[])
            data[field.name] = field.widget.pre_parse_request(field.attr,d)
    return dottedDict(data)


class FormsError(Exception):
    """
    Base class for all Forms errors. A single string, message, is accepted and
    stored as an attribute.
    
    The message is not passed on to the Exception base class because it doesn't
    seem to be able to handle unicode at all.
    """
    def __init__(self, message):
        Exception.__init__(self, message)
        self.message = message


class FormError(FormsError):
    """
    Form validation error. Raise this, typically from a submit callback, to
    signal that the form (not an individual field) failed to validate.
    """
    pass
    
class NoActionError(FormsError):
    """
    Form validation error. Raise this, typically from a submit callback, to
    signal that the form (not an individual field) failed to validate.
    """
    pass
    
    
class FieldError(FormsError):
    """
    Base class for field-related exceptions. The failure message and the failing
    field name are stored as attributes.
    """
    def __init__(self, message, fieldName=None):
        FormsError.__init__(self, message)
        self.fieldName = fieldName

class ConversionError(FieldError):
    """
    Exception that signals that a type conversion failed.
    """
    pass        
    
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
    
    
class RequiredValidator(object):
    
    def validate(self, field, value):
        if value is None:
            raise FieldRequiredError, 'Required'

    
class LengthValidator(object):
    """Validate the length of the value is within a given range. 
    """
    
    def __init__(self, min=None, max=None, unit="characters"):
        self.min = min
        self.max = max
        self.unit = unit
        assert self.min is not None or self.max is not None
        
    def validationErrorMessage(self, field):
        if self.min is not None and self.max is None:
            return 'Must be at least %r %s'%(self.min, self.unit)
        if self.min is None and self.max is not None:
            return 'Must be at most %r %s'%(self.max, self.unit)
        return 'Must be between %r and %r %s'%(self.min, self.max, self.unit)
    
    def validate(self, field, value):
        if value is None:
            return
        length = len(value)
        if self.min is not None and length < self.min:
            raise FieldValidationError, self.validationErrorMessage(field)
        if self.max is not None and length > self.max:
            raise FieldValidationError, self.validationErrorMessage(field)
            
            
class RangeValidator(object):
    """Validate the size of the value is within is given range.
    """
    
    def __init__(self, min=None, max=None):
        self.min = min
        self.max = max
        assert self.min is not None or self.max is not None
        
    def validationErrorMessage(self, field):
        if self.min is not None and self.max is None:
            return 'Must be %r or greater'%(self.min,)
        if self.min is None and self.max is not None:
            return 'Must be %r or less'%(self.max,)
        return 'Must be between %r and %r'%(self.min, self.max)
    
    def validate(self, field, value):
        if value is None:
            return
        if self.min is not None and value < self.min:
            raise FieldValidationError, self.validationErrorMessage(field)
        if self.max is not None and value > self.max:
            raise FieldValidationError, self.validationErrorMessage(field)

      
class PatternValidator(object):
    """Validate the value is a certain pattern.
    
    The required pattern is defined as a regular expression. The regex will be
    compiled automatically if necessary.
    """
    
    def __init__(self, regex):
        self.regex = regex
        
    def validate(self, field, value):
        if value is None:
            return
        # If it doesn't look like a regex object then compile it now
        if not hasattr(self.regex, 'match'):
            self.regex = re.compile(self.regex)
        if self.regex.match(value) is None:
            raise FieldValidationError, 'Invalid format'



class CallableValidator(object):
    """
    A validator that delegates the validation of non-None values to a callable
    """

    def __init__(self, callable):
        self.callable = callable

    def validate(self, field, value):
        if value is None:
            return
        return self.callable(field, value)
        
            
