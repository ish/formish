import re
import schemaish
from formish.dottedDict import dottedDict

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
                attr[1].validate(requestData.get(newprefix,None))
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
            if hasattr(field,'fields'):
                convertDataToRequestData(field, data, requestData=requestData, errors=errors)
            else: 
                requestData[field.name] = field.widget.pre_render(field.attr,data.get(field.name,None))
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
            if hasattr(field,'fields'):
                convertRequestDataToData(field, requestData, data=data, errors=errors)
            else: 
                # This needs to be cleverer... 
                x = field.widget.convert(field.attr,requestData.get(field.name,[]))
                data[field.name] = x
        except (schemaish.Invalid, FieldValidationError), e:
            errors[field.name] = e
    return data

def preParseRequestData(formStructure, requestData, data=None):
    if data is None:
        data = {}
    for field in formStructure.fields:
        if hasattr(field,'fields'):
            preParseRequestData(field, requestData, data=data)
        else: 
            # This needs to be cleverer...
            d = requestData.get(field.name,[])
            x = field.widget.pre_parse_request(field.attr,d)
            data[field.name] = x
    return data
    

class FormishError(Exception):
    """
    Base class for all Forms errors. A single string, message, is accepted and
    stored as an attribute.
    
    The message is not passed on to the Exception base class because it doesn't
    seem to be able to handle unicode at all.
    """
    def __init__(self, message):
        Exception.__init__(self, message)
        self.message = message


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
        FormishError.__init__(self, message)
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
        
            
